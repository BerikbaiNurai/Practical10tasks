import json
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, status, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Annotated
import aiofiles
from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI()

origins = ["http://localhost:3000"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

DB_FILE = "data/posts.json"

FAKE_USERS_DB = {
    "user1": {"id": "1", "username": "user1", "password": "password1"},
    "user2": {"id": "2", "username": "user2", "password": "password2"},
}

class Post(BaseModel):
    id: str
    text: str
    timestamp: datetime
    owner_id: str
    owner_username: str

class PostCreate(BaseModel):
    text: str

class User(BaseModel):
    id: str
    username: str

async def read_posts() -> List[Post]:
    async with aiofiles.open(DB_FILE, mode='r', encoding='utf-8') as f:
        content = await f.read()
        return [Post(**item) for item in json.loads(content)] if content else []

async def write_posts(posts: List[Post]):
    export_data = [post.model_dump(mode='json') for post in posts]
    async with aiofiles.open(DB_FILE, mode='w', encoding='utf-8') as f:
        await f.write(json.dumps(export_data, indent=4, ensure_ascii=False))

async def get_current_user(authorization: Annotated[str, Header()]) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid scheme")

    token = authorization.split(" ")[1]
    user_data = FAKE_USERS_DB.get(token)

    if not user_data:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    return User(**{"id": user_data["id"], "username": user_data["username"]})

@app.post("/api/login")
async def login(form_data: Dict[str, str]):
    username = form_data.get("username")
    password = form_data.get("password")
    user = FAKE_USERS_DB.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect username or password")

    return {"access_token": user["username"], "token_type": "bearer", "user": {"id": user["id"], "username": user["username"]}}

@app.get("/api/posts", response_model=List[Post])
async def list_posts():
    return get_posts_db()

@app.post("/api/posts", response_model=Post, status_code=201)
async def create_post(post_data: PostCreate, current_user: Annotated[User, Depends(get_current_user)]):
    return create_post_db(post_data, current_user)

@app.delete("/api/posts/{post_id}", status_code=204)
async def delete_post(post_id: str, current_user: Annotated[User, Depends(get_current_user)]):
    delete_post_db(post_id, current_user)
    return

@app.get("/api/users/{username}/posts", response_model=List[Post])
async def get_user_posts(username: str):
    db = SessionLocal()
    try:
        posts = db.query(PostDB).filter(PostDB.owner_username == username).order_by(PostDB.timestamp.desc()).all()
        return [Post(
            id=p.id,
            text=p.text,
            timestamp=p.timestamp,
            owner_id=p.owner_id,
            owner_username=p.owner_username
        ) for p in posts]
    finally:
        db.close()

@app.post("/api/posts/{post_id}/like", status_code=204)
async def like_post(post_id: str, current_user: Annotated[User, Depends(get_current_user)]):
    like_post_db(post_id, current_user)
    return Response(status_code=204)

@app.delete("/api/posts/{post_id}/like", status_code=204)
async def unlike_post(post_id: str, current_user: Annotated[User, Depends(get_current_user)]):
    unlike_post_db(post_id, current_user)
    return Response(status_code=204)

@app.get("/api/posts/{post_id}/likes-count")
async def get_post_likes_count(post_id: str):
    return {"count": get_likes_count(post_id)}

@app.get("/api/posts/{post_id}/liked-by-me")
async def get_post_liked_by_me(post_id: str, current_user: Annotated[User, Depends(get_current_user)]):
    return {"liked": is_post_liked_by_user(post_id, current_user)}

SQLALCHEMY_DATABASE_URL = "sqlite:///./data/app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PostDB(Base):
    __tablename__ = "posts"
    id = Column(String, primary_key=True, index=True)
    text = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    owner_id = Column(String, nullable=False)
    owner_username = Column(String, nullable=False)

class LikeDB(Base):
    __tablename__ = "likes"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    post_id = Column(String, ForeignKey("posts.id"), nullable=False)
    __table_args__ = (UniqueConstraint("user_id", "post_id", name="unique_user_post"),)

def get_posts_db():
    db = SessionLocal()
    try:
        posts = db.query(PostDB).order_by(PostDB.timestamp.desc()).all()
        return [Post(
            id=p.id,
            text=p.text,
            timestamp=p.timestamp,
            owner_id=p.owner_id,
            owner_username=p.owner_username
        ) for p in posts]
    finally:
        db.close()

def create_post_db(post_data: PostCreate, user: User):
    db = SessionLocal()
    try:
        new_post = PostDB(
            id=str(uuid.uuid4()),
            text=post_data.text,
            timestamp=datetime.now(timezone.utc),
            owner_id=user.id,
            owner_username=user.username
        )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return Post(
            id=new_post.id,
            text=new_post.text,
            timestamp=new_post.timestamp,
            owner_id=new_post.owner_id,
            owner_username=new_post.owner_username
        )
    finally:
        db.close()

def delete_post_db(post_id: str, user: User):
    db = SessionLocal()
    try:
        post = db.query(PostDB).filter(PostDB.id == post_id).first()
        if not post:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
        if post.owner_id != user.id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized to delete this post")
        db.delete(post)
        db.commit()
    finally:
        db.close()

def like_post_db(post_id: str, user: User):
    db = SessionLocal()
    try:
        post = db.query(PostDB).filter(PostDB.id == post_id).first()
        if not post:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
        existing = db.query(LikeDB).filter(LikeDB.user_id == user.id, LikeDB.post_id == post_id).first()
        if existing:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Already liked")
        like = LikeDB(id=str(uuid.uuid4()), user_id=user.id, post_id=post_id)
        db.add(like)
        db.commit()
    finally:
        db.close()

def unlike_post_db(post_id: str, user: User):
    db = SessionLocal()
    try:
        like = db.query(LikeDB).filter(LikeDB.user_id == user.id, LikeDB.post_id == post_id).first()
        if not like:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Like not found")
        db.delete(like)
        db.commit()
    finally:
        db.close()

def get_likes_count(post_id: str) -> int:
    db = SessionLocal()
    try:
        return db.query(LikeDB).filter(LikeDB.post_id == post_id).count()
    finally:
        db.close()

def is_post_liked_by_user(post_id: str, user: User) -> bool:
    db = SessionLocal()
    try:
        return db.query(LikeDB).filter(LikeDB.user_id == user.id, LikeDB.post_id == post_id).first() is not None
    finally:
        db.close()