from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ChatRequest, ChatResponse, TaskCreate, TaskResponse
from app.services.chatbot_service import chatbot_service
from app import crud

router = APIRouter(prefix="/api/chat", tags=["Chatbot"])

@router.post("", response_model=ChatResponse, summary="Gửi tin nhắn tới Trợ lý AI")
def send_chat_message(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Xử lý câu lệnh hoặc câu hỏi từ người dùng.
    Có khả năng tự động tạo task, tìm kiếm task, đánh dấu hoàn thành, xóa task hoặc tóm tắt tiến độ.
    """
    return chatbot_service.handle_message(request, db)

@router.get("/suggestions", response_model=List[str], summary="Lấy danh sách các câu hỏi/lệnh gợi ý")
def get_chat_suggestions():
    return [
        "📋 Danh sách các task cần làm",
        "✨ Tạo task Nộp báo cáo tuần trước ngày mai ưu tiên cao",
        "📊 Tóm tắt tiến độ công việc hiện tại",
        "💡 Gợi ý kế hoạch làm ứng dụng bán hàng",
        "🔥 Xem các task ưu tiên cao (high priority)",
        "❓ Hướng dẫn sử dụng chatbot"
    ]

@router.post("/batch-create", response_model=List[TaskResponse], status_code=status.HTTP_201_CREATED, summary="Tạo nhiều task cùng lúc từ gợi ý của chatbot")
def batch_create_tasks(tasks_in: List[TaskCreate], db: Session = Depends(get_db)):
    created_tasks = []
    for task_in in tasks_in:
        created = crud.create_task(db, task_in)
        created_tasks.append(created)
    return created_tasks
