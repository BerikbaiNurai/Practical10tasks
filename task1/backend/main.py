import uuid
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TodoItem(BaseModel):
    id: str
    task: str
    completed: bool = False

class TodoCreate(BaseModel):
    task: str

class TodoUpdate(BaseModel):
    task: str

fake_todo_db: List[TodoItem] = []

@app.get("/api/todos", response_model=List[TodoItem])
async def get_all_todos():
    return fake_todo_db

@app.post("/api/todos", response_model=TodoItem, status_code=201)
async def create_todo(todo_data: TodoCreate):
    new_todo = TodoItem(
        id=str(uuid.uuid4()),
        task=todo_data.task,
        completed=False
    )
    fake_todo_db.append(new_todo)
    return new_todo

@app.patch("/api/todos/{todo_id}", response_model=TodoItem)
async def toggle_todo(todo_id: str):
    for todo in fake_todo_db:
        if todo.id == todo_id:
            todo.completed = not todo.completed
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.put("/api/todos/{todo_id}", response_model=TodoItem)
async def update_todo(todo_id: str, updated_data: TodoUpdate):
    for todo in fake_todo_db:
        if todo.id == todo_id:
            todo.task = updated_data.task
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/api/todos/{todo_id}", status_code=204)
async def delete_todo(todo_id: str):
    for todo in fake_todo_db:
        if todo.id == todo_id:
            fake_todo_db.remove(todo)
            return
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/api/todos/completed", status_code=204)
async def delete_completed_todos():
    print("DELETE /api/todos/completed called", flush=True)
    global fake_todo_db
    fake_todo_db = [todo for todo in fake_todo_db if not (todo.completed if isinstance(todo, TodoItem) else todo.get("completed", False))]
    return

@app.get("/")
async def root():
    return {"message": "FastAPI To-Do Backend is running!"}
