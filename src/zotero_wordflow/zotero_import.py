from __future__ import annotations

import random
import shutil
import sqlite3
import subprocess
import time
from pathlib import Path
from typing import Any


def random_zotero_key(length: int = 8) -> str:
    alphabet = "23456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join(random.choice(alphabet) for _ in range(length))


def stop_zotero() -> None:
    subprocess.run(["taskkill", "/IM", "zotero.exe"], check=False, capture_output=True, text=True)
    time.sleep(3)
    remaining = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq zotero.exe"],
        check=False,
        capture_output=True,
        text=True,
    )
    if "zotero.exe" in remaining.stdout.lower():
        subprocess.run(["taskkill", "/IM", "zotero.exe", "/F"], check=False, capture_output=True, text=True)
        time.sleep(3)


def start_zotero(zotero_exe: Path) -> None:
    subprocess.Popen([str(zotero_exe)])
    time.sleep(6)


def backup_zotero_db(output_dir: Path, zotero_data_dir: Path) -> Path:
    backup_dir = output_dir / "zotero_backup_preimport"
    backup_dir.mkdir(parents=True, exist_ok=True)
    for name in ("zotero.sqlite", "zotero.sqlite-wal", "zotero.sqlite-shm"):
        src = zotero_data_dir / name
        if src.exists():
            shutil.copy2(src, backup_dir / name)
    return backup_dir


def restore_zotero_db(backup_dir: Path, zotero_data_dir: Path) -> None:
    for name in ("zotero.sqlite", "zotero.sqlite-wal", "zotero.sqlite-shm"):
        src = backup_dir / name
        dst = zotero_data_dir / name
        if src.exists():
            shutil.copy2(src, dst)
        elif dst.exists() and name.endswith(("-wal", "-shm")):
            dst.unlink()


def get_lookup_id(cursor: sqlite3.Cursor, table: str, select_col: str, where_col: str, value: str) -> int:
    cursor.execute(f"SELECT {select_col} FROM {table} WHERE {where_col} = ? LIMIT 1", (value,))
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"Missing lookup in {table}: {value}")
    return int(row[0])


def ensure_creator(cursor: sqlite3.Cursor, first_name: str, last_name: str) -> int:
    cursor.execute(
        """
        SELECT creatorID
        FROM creators
        WHERE firstName = ? AND lastName = ? AND fieldMode = 0
        LIMIT 1
        """,
        (first_name, last_name),
    )
    row = cursor.fetchone()
    if row:
        return int(row[0])
    cursor.execute("INSERT INTO creators (firstName, lastName, fieldMode) VALUES (?, ?, 0)", (first_name, last_name))
    return int(cursor.lastrowid)


def ensure_item_value(cursor: sqlite3.Cursor, value: str) -> int:
    cursor.execute("SELECT valueID FROM itemDataValues WHERE value = ? LIMIT 1", (value,))
    row = cursor.fetchone()
    if row:
        return int(row[0])
    cursor.execute("INSERT INTO itemDataValues (value) VALUES (?)", (value,))
    return int(cursor.lastrowid)


def find_existing_item(cursor: sqlite3.Cursor, ref: dict[str, Any], allow_title_match_reuse: bool) -> int | None:
    cursor.execute(
        """
        SELECT d.itemID
        FROM itemData d
        JOIN fieldsCombined f ON d.fieldID = f.fieldID
        JOIN itemDataValues v ON d.valueID = v.valueID
        WHERE f.fieldName = 'DOI'
          AND lower(v.value) IN (?, ?)
        LIMIT 1
        """,
        (ref["doi"], f"https://doi.org/{ref['doi']}"),
    )
    row = cursor.fetchone()
    if row:
        return int(row[0])
    if not allow_title_match_reuse:
        return None
    cursor.execute(
        """
        SELECT d.itemID
        FROM itemData d
        JOIN fieldsCombined f ON d.fieldID = f.fieldID
        JOIN itemDataValues v ON d.valueID = v.valueID
        WHERE f.fieldName = 'title' AND v.value = ?
        LIMIT 1
        """,
        (ref["title"],),
    )
    row = cursor.fetchone()
    return int(row[0]) if row else None


def ensure_collection(cursor: sqlite3.Cursor, collection_name: str) -> int:
    cursor.execute(
        "SELECT collectionID FROM collections WHERE collectionName = ? AND libraryID = 1 LIMIT 1",
        (collection_name,),
    )
    row = cursor.fetchone()
    if row:
        return int(row[0])
    cursor.execute(
        """
        INSERT INTO collections (collectionName, parentCollectionID, libraryID, key, version, synced)
        VALUES (?, NULL, 1, ?, 0, 0)
        """,
        (collection_name, random_zotero_key()),
    )
    return int(cursor.lastrowid)


def add_item_to_collection(cursor: sqlite3.Cursor, collection_id: int, item_id: int) -> None:
    cursor.execute("SELECT 1 FROM collectionItems WHERE collectionID = ? AND itemID = ?", (collection_id, item_id))
    if cursor.fetchone():
        return
    cursor.execute("SELECT COALESCE(MAX(orderIndex), -1) + 1 FROM collectionItems WHERE collectionID = ?", (collection_id,))
    order_index = int(cursor.fetchone()[0])
    cursor.execute(
        "INSERT INTO collectionItems (collectionID, itemID, orderIndex) VALUES (?, ?, ?)",
        (collection_id, item_id, order_index),
    )


def insert_reference(cursor: sqlite3.Cursor, ref: dict[str, Any], allow_title_match_reuse: bool) -> int:
    existing_id = find_existing_item(cursor, ref, allow_title_match_reuse)
    if existing_id:
        return existing_id
    item_type_id = get_lookup_id(cursor, "itemTypesCombined", "itemTypeID", "typeName", "journalArticle")
    author_type_id = get_lookup_id(cursor, "creatorTypes", "creatorTypeID", "creatorType", "author")
    cursor.execute(
        "INSERT INTO items (itemTypeID, libraryID, key, version, synced) VALUES (?, 1, ?, 0, 0)",
        (item_type_id, random_zotero_key()),
    )
    item_id = int(cursor.lastrowid)
    field_map = {
        "title": ref["title"],
        "publicationTitle": ref["journal"],
        "date": str(ref["year"]),
        "volume": ref["volume"],
        "issue": ref["issue"],
        "pages": ref["pages"],
        "DOI": ref["doi"],
        "url": ref["url"],
    }
    for field_name, value in field_map.items():
        if not value:
            continue
        field_id = get_lookup_id(cursor, "fieldsCombined", "fieldID", "fieldName", field_name)
        value_id = ensure_item_value(cursor, value)
        cursor.execute("INSERT INTO itemData (itemID, fieldID, valueID) VALUES (?, ?, ?)", (item_id, field_id, value_id))
    for order_index, author in enumerate(ref["authors"]):
        creator_id = ensure_creator(cursor, author["given"], author["family"])
        cursor.execute(
            "INSERT INTO itemCreators (itemID, creatorID, creatorTypeID, orderIndex) VALUES (?, ?, ?, ?)",
            (item_id, creator_id, author_type_id, order_index),
        )
    return item_id


def get_item_key(cursor: sqlite3.Cursor, item_id: int) -> str:
    cursor.execute("SELECT key FROM items WHERE itemID = ?", (item_id,))
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"Missing key for item {item_id}")
    return str(row[0])


def import_to_zotero(
    refs: list[dict[str, Any]],
    collection_name: str,
    zotero_data_dir: Path,
    local_user_key: str,
    allow_title_match_reuse: bool,
) -> dict[str, Any]:
    conn = sqlite3.connect(zotero_data_dir / "zotero.sqlite")
    try:
        cursor = conn.cursor()
        collection_id = ensure_collection(cursor, collection_name)
        items = []
        for ref in refs:
            item_id = insert_reference(cursor, ref, allow_title_match_reuse)
            add_item_to_collection(cursor, collection_id, item_id)
            items.append(
                {
                    "cite_key": ref["cite_key"],
                    "title": ref["title"],
                    "doi": ref["doi"],
                    "item_id": item_id,
                    "uri": f"http://zotero.org/users/local/{local_user_key}/items/{get_item_key(cursor, item_id)}",
                }
            )
        conn.commit()
        return {"collection_id": collection_id, "collection_name": collection_name, "items": items}
    finally:
        conn.close()
