from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List
import os
import json
import uuid

app = FastAPI()

origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

POLL_FILE = "polls.json"

class PollOption(BaseModel):
    label: str
    votes: int = 0

class Poll(BaseModel):
    id: str
    question: str
    options: Dict[str, PollOption]

class CreatePollRequest(BaseModel):
    question: str
    options: List[str]

def load_polls() -> List[Poll]:
    if os.path.exists(POLL_FILE):
        with open(POLL_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Poll(**poll) for poll in data]
    return []

def save_polls(polls: List[Poll]):
    with open(POLL_FILE, "w", encoding="utf-8") as f:
        json.dump([poll.dict() for poll in polls], f, ensure_ascii=False, indent=2)

polls: List[Poll] = load_polls()

@app.get("/api/poll/latest", response_model=Poll)
def get_latest_poll():
    if not polls:
        raise HTTPException(status_code=404, detail="Опросов нет")
    return polls[-1]

@app.post("/api/poll/create", response_model=Poll)
def create_poll(payload: CreatePollRequest):
    if len(payload.options) < 2:
        raise HTTPException(status_code=400, detail="Минимум 2 варианта")
    poll_id = str(uuid.uuid4())
    options_dict = {opt: PollOption(label=opt) for opt in payload.options}
    poll = Poll(id=poll_id, question=payload.question, options=options_dict)
    polls.append(poll)
    save_polls(polls)
    return poll

@app.post("/api/poll/vote/{poll_id}/{option_key}", response_model=Poll)
def vote_poll(poll_id: str, option_key: str):
    for poll in polls:
        if poll.id == poll_id:
            if option_key not in poll.options:
                raise HTTPException(status_code=404, detail="Опция не найдена")
            poll.options[option_key].votes += 1
            save_polls(polls)
            return poll
    raise HTTPException(status_code=404, detail="Опрос не найден")
