from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import TaskCreate, TaskUpdate, TaskResponse
from app import crud

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

@router.get("", response_model=List[TaskResponse], summary="Lấy danh sách công việc")
def list_tasks(
    status: Optional[str] = Query(None, description="Lọc theo trạng thái: pending hoặc completed"),
    priority: Optional[str] = Query(None, description="Lọc theo ưu tiên: low, medium, high"),
    search: Optional[str] = Query(None, description="Tìm kiếm từ khóa"),
    db: Session = Depends(get_db)
):
    return crud.get_tasks(db, status=status, priority=priority, search=search)

@router.get("/{task_id}", response_model=TaskResponse, summary="Lấy chi tiết một công việc")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Công việc có id={task_id} không tồn tại"
        )
    return task

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, summary="Tạo công việc mới")
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, task_in=task_in)

@router.put("/{task_id}", response_model=TaskResponse, summary="Cập nhật toàn bộ/một phần công việc")
def update_task(task_id: int, task_in: TaskUpdate, db: Session = Depends(get_db)):
    updated_task = crud.update_task(db, task_id=task_id, task_in=task_in)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Công việc có id={task_id} không tồn tại để cập nhật"
        )
    return updated_task

@router.patch("/{task_id}/complete", response_model=TaskResponse, summary="Đánh dấu hoàn thành / Hoàn tác")
def toggle_task_complete(task_id: int, db: Session = Depends(get_db)):
    task = crud.toggle_complete_task(db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Công việc có id={task_id} không tồn tại"
        )
    return task

@router.delete("/{task_id}", status_code=status.HTTP_200_OK, summary="Xóa một công việc")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    success = crud.delete_task(db, task_id=task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Công việc có id={task_id} không tồn tại để xóa"
        )
    return {"message": f"Đã xóa công việc {task_id} thành công"}
