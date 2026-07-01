from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Todo

router = APIRouter(prefix="/api/todos", tags=["todos"])


class TodoCreate(BaseModel):
    title: str


class TodoOut(BaseModel):
    id: int
    title: str
    done: bool

    class Config:
        from_attributes = True


@router.get("", response_model=list[TodoOut])
def list_todos(db: Session = Depends(get_db)):
    return db.query(Todo).order_by(Todo.created_at).all()


@router.post("", response_model=TodoOut)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = Todo(title=todo.title)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


@router.patch("/{todo_id}/toggle", response_model=TodoOut)
def toggle_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.get(Todo, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db_todo.done = not db_todo.done
    db.commit()
    db.refresh(db_todo)
    return db_todo


@router.delete("/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.get(Todo, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(db_todo)
    db.commit()
    return {"ok": True}
