import json
import uuid
import os
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import aiofiles

app = FastAPI()

origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

DB_FILE = "data/guestbook.json"
os.makedirs("data", exist_ok=True)

class GuestbookEntry(BaseModel):
    id: str
    name: str
    message: str
    timestamp: datetime

class EntryCreate(BaseModel):
    name: str
    message: str

class EntryUpdate(BaseModel):
    message: Optional[str] = None

async def read_db() -> List[GuestbookEntry]:
    if not os.path.exists(DB_FILE):
        async with aiofiles.open(DB_FILE, mode='w', encoding='utf-8') as f:
            await f.write('[]')
        return []

    async with aiofiles.open(DB_FILE, mode='r', encoding='utf-8') as f:
        content = await f.read()
        if not content.strip():
            return []
        try:
            data = json.loads(content)
            return [GuestbookEntry(**e) for e in data]
        except Exception:
            raise HTTPException(status_code=500, detail="Ошибка чтения базы guestbook.json")

async def write_db(entries: List[GuestbookEntry]):
    async with aiofiles.open(DB_FILE, mode='w', encoding='utf-8') as f:
        export_data = []
        for e in entries:
            d = e.dict()
            if isinstance(d["timestamp"], datetime):
                d["timestamp"] = d["timestamp"].isoformat()
            export_data.append(d)
        await f.write(json.dumps(export_data, indent=4, ensure_ascii=False))

@app.get("/api/entries")
async def get_entries(page: int = Query(1, ge=1), limit: int = Query(5, ge=1)):
    entries = await read_db()
    start = (page - 1) * limit
    end = start + limit
    return entries[start:end]

@app.post("/api/entries", response_model=GuestbookEntry)
async def create_entry(data: EntryCreate):
    if not data.name.strip() or not data.message.strip():
        raise HTTPException(status_code=400, detail="Имя и сообщение не могут быть пустыми.")
    
    entries = await read_db()
    new_entry = GuestbookEntry(
        id=str(uuid.uuid4()),
        name=data.name.strip(),
        message=data.message.strip(),
        timestamp=datetime.now(timezone.utc)
    )
    entries.append(new_entry)
    await write_db(entries)
    return new_entry

@app.delete("/api/entries/{entry_id}")
async def delete_entry(entry_id: str):
    entries = await read_db()
    filtered = [e for e in entries if e.id != entry_id]
    if len(filtered) == len(entries):
        raise HTTPException(status_code=404, detail="Запись не найдена")
    await write_db(filtered)
    return {"message": "Удалено"}

@app.put("/api/entries/{entry_id}", response_model=GuestbookEntry)
async def update_entry(entry_id: str, data: EntryUpdate):
    entries = await read_db()
    for entry in entries:
        if entry.id == entry_id:
            if data.message is not None:
                entry.message = data.message.strip()
            await write_db(entries)
            return entry
    raise HTTPException(status_code=404, detail="Запись не найдена")