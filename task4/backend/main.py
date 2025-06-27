import secrets
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional

app = FastAPI()


origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

url_db = {}

EXPIRATION_DAYS = 7 

class URLCreate(BaseModel):
    long_url: HttpUrl
    custom_code: Optional[str] = None

@app.post("/api/shorten")
def create_short_url(url_data: URLCreate, request: Request):
    long_url = str(url_data.long_url)

    if url_data.custom_code:
        short_code = url_data.custom_code
        if short_code in url_db:
            raise HTTPException(status_code=400, detail="Custom short code already taken")
    else:
        short_code = secrets.token_urlsafe(6)
        while short_code in url_db:
            short_code = secrets.token_urlsafe(6)

    url_db[short_code] = {
        "long_url": long_url,
        "clicks": 0,
        "created_at": datetime.utcnow()
    }

    short_url = f"{request.base_url}{short_code}"
    return {
        "short_url": short_url,
        "clicks": 0
    }

@app.get("/{short_code}")
def redirect_to_long_url(short_code: str):
    entry = url_db.get(short_code)
    if not entry:
        raise HTTPException(status_code=404, detail="Short URL not found")

    if datetime.utcnow() - entry["created_at"] > timedelta(days=EXPIRATION_DAYS):
        raise HTTPException(status_code=404, detail="Short URL has expired")

    entry["clicks"] += 1

    return RedirectResponse(url=entry["long_url"])

@app.get("/api/stats/{short_code}")
def get_stats(short_code: str):
    entry = url_db.get(short_code)
    if not entry:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return {
        "short_code": short_code,
        "long_url": entry["long_url"],
        "clicks": entry["clicks"],
        "created_at": entry["created_at"].isoformat()
    }