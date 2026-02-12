from datetime import datetime, timedelta
import secrets

import bcrypt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from connection import get_db_session
from config import TOKEN_EXPIRE_MINUTES
from database import init_db
from models import Todo, Token, User
from schemas import (
    AuthOut,
    TodoCreate,
    TodoOut,
    TodoUpdate,
    UserCreate,
    UserOut,
)

app = FastAPI(title="Todo API")
security = HTTPBearer()


@app.on_event("startup")
def on_startup():
    init_db()


def create_auth_token(session: Session, user: User) -> Token:
    created_at = datetime.utcnow()
    expires_at = created_at + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    token_value = secrets.token_urlsafe(32)
    auth_token = Token(
        user_id=user.id,
        token=token_value,
        created_at=created_at,
        expires_at=expires_at,
    )
    session.add(auth_token)
    session.commit()
    session.refresh(auth_token)
    return auth_token


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_db_session),
) -> User:
    stmt = select(Token).where(Token.token == credentials.credentials)
    auth_token = session.execute(stmt).scalar_one_or_none()
    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
        )

    if auth_token.expires_at <= datetime.utcnow():
        session.delete(auth_token)
        session.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )

    return auth_token.user


@app.post("/auth/register", response_model=UserOut)
def register(payload: UserCreate, session: Session = Depends(get_db_session)):
    existing = session.execute(
        select(User).where(User.username == payload.username)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    password_hash = bcrypt.hashpw(
        payload.password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")
    user = User(username=payload.username, password_hash=password_hash)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.post("/auth/login", response_model=AuthOut)
def login(payload: UserCreate, session: Session = Depends(get_db_session)):
    user = session.execute(
        select(User).where(User.username == payload.username)
    ).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    ok = bcrypt.checkpw(
        payload.password.encode("utf-8"),
        user.password_hash.encode("utf-8"),
    )
    if not ok:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    auth_token = create_auth_token(session=session, user=user)
    return AuthOut(
        user_id=user.id,
        username=user.username,
        token=auth_token.token,
        expires_at=auth_token.expires_at,
    )


@app.get("/todos", response_model=list[TodoOut])
def list_todos(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    stmt = select(Todo).where(Todo.user_id == current_user.id).order_by(Todo.id)
    return list(session.execute(stmt).scalars().all())


@app.post("/todos", response_model=TodoOut, status_code=201)
def create_todo(
    payload: TodoCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    todo = Todo(user_id=current_user.id, task=payload.task, is_completed=False)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@app.patch("/todos/{todo_id}", response_model=TodoOut)
def update_todo(
    todo_id: int,
    payload: TodoUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    todo = session.execute(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    ).scalar_one_or_none()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if payload.task is not None:
        todo.task = payload.task
    if payload.is_completed is not None:
        todo.is_completed = payload.is_completed
    session.commit()
    session.refresh(todo)
    return todo


@app.post("/todos/{todo_id}/toggle", response_model=TodoOut)
def toggle_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    todo = session.execute(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    ).scalar_one_or_none()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.is_completed = not todo.is_completed
    session.commit()
    session.refresh(todo)
    return todo


@app.delete("/todos/{todo_id}")
def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    todo = session.execute(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    ).scalar_one_or_none()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    session.delete(todo)
    session.commit()
    return {"status": "deleted"}
