from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app.models import Todo
from app.schemas import TodoCreate, TodoRead

app = FastAPI(title="Just Call Todo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=(
        r"http://("
        r"localhost|127\.0\.0\.1|0\.0\.0\.0|"
        r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
        r"172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}|"
        r"192\.168\.\d{1,3}\.\d{1,3}"
        r"):(5173|5174|5175|5176|5177|5178|5179)"
    ),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/todos", response_model=list[TodoRead])
def list_todos(db: Annotated[Session, Depends(get_db)]) -> list[Todo]:
    statement = select(Todo).order_by(Todo.created_at.desc(), Todo.id.desc())
    return list(db.scalars(statement))


@app.post("/todos", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate, db: Annotated[Session, Depends(get_db)]) -> Todo:
    todo = Todo(title=payload.title.strip())
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: Annotated[Session, Depends(get_db)]) -> None:
    todo = db.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    db.delete(todo)
    db.commit()
