import bcrypt
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from connection import get_db_session
from database import init_db
from models import Todo, User
from schemas import (
    TodoCreate,
    TodoOut,
    TodoUpdate,
    AuthOut,
    UserCreate,
    UserOut,
)

app = FastAPI(title="Todo API")


@app.on_event("startup")
def on_startup():
    init_db()


def get_current_user(
    session: Session = Depends(get_db_session),
    user_id: int | None = None,
) -> User:
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing user_id",
        )
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


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
    return AuthOut(user_id=user.id, username=user.username)


@app.get("/todos", response_model=list[TodoOut])
def list_todos(
    user_id: int,
    session: Session = Depends(get_db_session),
):
    current_user = get_current_user(session=session, user_id=user_id)
    stmt = select(Todo).where(Todo.user_id == current_user.id).order_by(Todo.id)
    return list(session.execute(stmt).scalars().all())


@app.post("/todos", response_model=TodoOut, status_code=201)
def create_todo(
    payload: TodoCreate,
    user_id: int,
    session: Session = Depends(get_db_session),
):
    current_user = get_current_user(session=session, user_id=user_id)
    todo = Todo(user_id=current_user.id, task=payload.task, is_completed=False)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@app.patch("/todos/{todo_id}", response_model=TodoOut)
def update_todo(
    todo_id: int,
    payload: TodoUpdate,
    user_id: int,
    session: Session = Depends(get_db_session),
):
    current_user = get_current_user(session=session, user_id=user_id)
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
    user_id: int,
    session: Session = Depends(get_db_session),
):
    current_user = get_current_user(session=session, user_id=user_id)
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
    user_id: int,
    session: Session = Depends(get_db_session),
):
    current_user = get_current_user(session=session, user_id=user_id)
    todo = session.execute(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    ).scalar_one_or_none()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    session.delete(todo)
    session.commit()
    return {"status": "deleted"}
