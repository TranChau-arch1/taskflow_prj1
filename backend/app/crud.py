from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Task
from app.schemas import TaskCreate, TaskUpdate

def get_tasks(
    db: Session,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None
) -> List[Task]:
    query = db.query(Task)
    if status and status != "all":
        query = query.filter(Task.status == status)
    if priority and priority != "all":
        query = query.filter(Task.priority == priority)
    if search:
        query = query.filter(Task.title.ilike(f"%{search}%") | Task.description.ilike(f"%{search}%"))
    
    # Sort by created_at desc
    return query.order_by(desc(Task.created_at)).all()

def get_task(db: Session, task_id: int) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()

def create_task(db: Session, task_in: TaskCreate) -> Task:
    db_task = Task(
        title=task_in.title.strip(),
        description=task_in.description.strip() if task_in.description else None,
        status=task_in.status,
        priority=task_in.priority,
        due_date=task_in.due_date,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_in: TaskUpdate) -> Optional[Task]:
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "title" and value is not None:
            value = value.strip()
        if field == "description" and value is not None:
            value = value.strip()
        setattr(db_task, field, value)
        
    db.commit()
    db.refresh(db_task)
    return db_task

def toggle_complete_task(db: Session, task_id: int) -> Optional[Task]:
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    db_task.status = "pending" if db_task.status == "completed" else "completed"
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int) -> bool:
    db_task = get_task(db, task_id)
    if not db_task:
        return False
    db.delete(db_task)
    db.commit()
    return True
