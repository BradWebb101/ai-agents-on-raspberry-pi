from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from mcp.server.fastmcp import FastMCP
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import Any, Dict, List
import mcp

DATABASE_API_URL = "http://sqlite-api:8000"

print("[MCP SERVER] Starting FastAPI app...")

app = FastAPI(title="SQLite MCP API with OAuth2 Proxy", lifespan=lambda app: mcp.session_manager.run())
mcp = FastMCP("sqlite-api", stateless_http=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend's origin(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@mcp.tool()
async def list_tables() -> List[str]:
    print("[MCP SERVER] list_tables called")
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{DATABASE_API_URL}/tables")
        resp.raise_for_status()
        print(f"[MCP SERVER] list_tables response: {resp.text}")
        return resp.json()

@mcp.tool()
async def get_all_rows(table_name: str) -> List[Dict[str, Any]]:
    print(f"[MCP SERVER] get_all_rows called for table: {table_name}")
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{DATABASE_API_URL}/table/{table_name}")
        resp.raise_for_status()
        print(f"[MCP SERVER] get_all_rows response: {resp.text}")
        return resp.json()

@mcp.tool()
async def get_row(table_name: str, row_id: int) -> Dict[str, Any]:
    print(f"[MCP SERVER] get_row called for table: {table_name}, row_id: {row_id}")
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{DATABASE_API_URL}/table/{table_name}/{row_id}")
        resp.raise_for_status()
        print(f"[MCP SERVER] get_row response: {resp.text}")
        return resp.json()

@mcp.tool()
async def insert_row(table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    print(f"[MCP SERVER] insert_row called for table: {table_name}, data: {data}")
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{DATABASE_API_URL}/table/{table_name}", json={"data": data})
        resp.raise_for_status()
        print(f"[MCP SERVER] insert_row response: {resp.text}")
        return resp.json()

@mcp.tool()
async def update_row(table_name: str, row_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    print(f"[MCP SERVER] update_row called for table: {table_name}, row_id: {row_id}, data: {data}")
    async with httpx.AsyncClient() as client:
        resp = await client.put(f"{DATABASE_API_URL}/table/{table_name}/{row_id}", json={"data": data})
        resp.raise_for_status()
        print(f"[MCP SERVER] update_row response: {resp.text}")
        return resp.json()

@mcp.tool()
async def delete_row(table_name: str, row_id: int) -> Dict[str, Any]:
    print(f"[MCP SERVER] delete_row called for table: {table_name}, row_id: {row_id}")
    async with httpx.AsyncClient() as client:
        resp = await client.delete(f"{DATABASE_API_URL}/table/{table_name}/{row_id}")
        resp.raise_for_status()
        print(f"[MCP SERVER] delete_row response: {resp.text}")
        return resp.json()

app.mount("/", mcp.streamable_http_app())

if __name__ == "__main__":
    print("[MCP SERVER] Running MCP server...")
    mcp.run(transport='streamable-http')
