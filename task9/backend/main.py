from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Annotated
import uuid
import time

app = FastAPI()

origins = ["http://localhost:3000"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

FAKE_USER = {"username": "user", "password": "password", "role": "admin"} 

TOKENS = {} 
TOKEN_LIFETIME_SECONDS = 3600 

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

async def token_verifier(authorization: Annotated[str, Header()], required_role: str = None):
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
        )
    token = authorization.split(" ")[1]
    user_data = TOKENS.get(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    if time.time() - user_data["created_at"] > TOKEN_LIFETIME_SECONDS:
        del TOKENS[token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    if required_role and user_data["role"] != required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return user_data

async def admin_token_verifier(authorization: Annotated[str, Header()]):
    return await token_verifier(authorization, required_role="admin")


@app.post("/api/login", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Проверяет логин/пароль и возвращает токен."""
    if form_data.username == FAKE_USER["username"] and form_data.password == FAKE_USER["password"]:
        access_token = str(uuid.uuid4())
        TOKENS[access_token] = {
            "username": FAKE_USER["username"],
            "role": FAKE_USER["role"],
            "created_at": time.time(),
        }
        return {"access_token": access_token, "token_type": "bearer", "role": FAKE_USER["role"]}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

@app.post("/api/logout")
async def logout(authorization: Annotated[str, Header()]):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication scheme")
    token = authorization.split(" ")[1]
    if token in TOKENS:
        del TOKENS[token]
    return {"message": "Logged out"}

@app.get("/api/secret-data")
async def get_secret_data(user_data: Annotated[dict, Depends(token_verifier)]):
    """Этот эндпоинт защищен. Доступ возможен только с валидным токеном."""
    return {"message": f"Привет, {user_data['username']}! Секретное сообщение: 42.", "role": user_data["role"]}

@app.get("/api/admin-data")
async def get_admin_data(user_data: Annotated[dict, Depends(admin_token_verifier)]):
    """Доступ только для админа."""
    return {"message": f"Привет, {user_data['username']}! Это админские данные.", "role": user_data["role"]}