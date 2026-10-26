from datetime import date, datetime
from typing import Optional, Literal, List
from pydantic import BaseModel, Field, ConfigDict

PriorityType = Literal["low", "medium", "high"]
StatusType = Literal["pending", "completed"]

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Tiêu đề công việc")
    description: Optional[str] = Field(None, description="Mô tả chi tiết")
    status: StatusType = Field(default="pending", description="Trạng thái công việc")
    priority: PriorityType = Field(default="medium", description="Mức độ ưu tiên")
    due_date: Optional[date] = Field(None, description="Ngày đến hạn (YYYY-MM-DD)")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[StatusType] = None
    priority: Optional[PriorityType] = None
    due_date: Optional[date] = None

class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HealthResponse(BaseModel):
    status: str
    database: str
    version: str

# Chatbot Schemas
class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Tin nhắn từ người dùng")
    history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Lịch sử trò chuyện gần nhất")

class ChatAction(BaseModel):
    type: Literal["create_task", "complete_task", "delete_task", "list_tasks", "suggest_tasks", "summary", "none"] = "none"
    task: Optional[TaskResponse] = None
    tasks: Optional[List[TaskResponse]] = None
    suggested_tasks: Optional[List[TaskCreate]] = None
    summary_data: Optional[dict] = None

class ChatResponse(BaseModel):
    reply: str
    action: Optional[ChatAction] = None
    llm_used: bool = False
    provider: Optional[str] = None
