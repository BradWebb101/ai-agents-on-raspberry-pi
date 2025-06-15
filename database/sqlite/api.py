from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
import sqlite3
from typing import List, Any, Dict
import os
from fastapi.middleware.cors import CORSMiddleware

DB_PATH = './database.db'
app = FastAPI(title="SQLite CRUD API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/tables", response_model=List[str])
def list_tables():
    conn = get_db_connection()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

@app.get("/table/{table_name}", response_model=List[Dict[str, Any]])
def get_all_rows(table_name: str):
    conn = get_db_connection()
    try:
        cursor = conn.execute(f"SELECT * FROM {table_name}")
        rows = [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    conn.close()
    return rows

@app.get("/table/{table_name}/{row_id}", response_model=Dict[str, Any])
def get_row(table_name: str, row_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.execute(f"SELECT * FROM {table_name} WHERE id=?", (row_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Row not found")
        result = dict(row)
    except sqlite3.Error as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    conn.close()
    return result

class RowData(BaseModel):
    data: Dict[str, Any]

@app.post("/table/{table_name}", response_model=Dict[str, Any])
def insert_row(table_name: str, row: RowData):
    conn = get_db_connection()
    keys = ','.join(row.data.keys())
    placeholders = ','.join(['?'] * len(row.data))
    values = tuple(row.data.values())
    try:
        cursor = conn.execute(f"INSERT INTO {table_name} ({keys}) VALUES ({placeholders})", values)
        conn.commit()
        row_id = cursor.lastrowid
        cursor = conn.execute(f"SELECT * FROM {table_name} WHERE id=?", (row_id,))
        result = dict(cursor.fetchone())
    except sqlite3.Error as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    conn.close()
    return result

@app.put("/table/{table_name}/{row_id}", response_model=Dict[str, Any])
def update_row(table_name: str, row_id: int, row: RowData):
    conn = get_db_connection()
    set_clause = ', '.join([f"{k}=?" for k in row.data.keys()])
    values = tuple(row.data.values()) + (row_id,)
    try:
        conn.execute(f"UPDATE {table_name} SET {set_clause} WHERE id=?", values)
        conn.commit()
        cursor = conn.execute(f"SELECT * FROM {table_name} WHERE id=?", (row_id,))
        updated = cursor.fetchone()
        if not updated:
            raise HTTPException(status_code=404, detail="Row not found")
        result = dict(updated)
    except sqlite3.Error as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    conn.close()
    return result

@app.delete("/table/{table_name}/{row_id}")
def delete_row(table_name: str, row_id: int):
    conn = get_db_connection()
    try:
        conn.execute(f"DELETE FROM {table_name} WHERE id=?", (row_id,))
        conn.commit()
    except sqlite3.Error as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    conn.close()
    return {"detail": "Row deleted"} 