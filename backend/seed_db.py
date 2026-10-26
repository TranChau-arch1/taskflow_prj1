import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from datetime import date, timedelta
from app.database import SessionLocal, engine, Base
from app.models import Task

# Ensure tables exist
Base.metadata.create_all(bind=engine)

def seed():
    db = SessionLocal()
    try:
        # Check if already has data
        existing_count = db.query(Task).count()
        if existing_count > 0:
            print(f"Database đã có sẵn {existing_count} công việc, bỏ qua seed data.")
            return

        today = date.today()
        sample_tasks = [
            Task(
                title="Khởi tạo dự án TaskFlow và kết nối API",
                description="Thiết lập monorepo với Vite React ở Frontend và FastAPI ở Backend.",
                status="completed",
                priority="high",
                due_date=today - timedelta(days=1),
            ),
            Task(
                title="Hoàn thiện các component và giao diện Dark Theme",
                description="Bao gồm TaskStats, TaskFilters, TaskList, TaskItem và TaskModal.",
                status="completed",
                priority="medium",
                due_date=today,
            ),
            Task(
                title="Tạo cơ sở dữ liệu PostgreSQL trên Neon",
                description="Đăng ký tài khoản Neon.tech, tạo database và lưu chuỗi DATABASE_URL.",
                status="pending",
                priority="high",
                due_date=today + timedelta(days=2),
            ),
            Task(
                title="Deploy Backend lên Render và Frontend lên Vercel",
                description="Cấu hình biến môi trường, định tuyến SPA và mở khóa CORS.",
                status="pending",
                priority="high",
                due_date=today + timedelta(days=3),
            ),
            Task(
                title="Viết tài liệu hướng dẫn và nghiệm thu 9 tiêu chí",
                description="Kiểm thử trên link domain công khai và cập nhật README.md.",
                status="pending",
                priority="low",
                due_date=today + timedelta(days=4),
            )
        ]

        db.add_all(sample_tasks)
        db.commit()
        print(f"Đã nạp thành công {len(sample_tasks)} công việc mẫu vào Database! 🎉")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
