import os
import re
import json
from datetime import date, datetime, timedelta
from typing import Optional, List, Tuple, Dict, Any
import httpx
from sqlalchemy.orm import Session

from app.models import Task
from app.schemas import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ChatAction,
    TaskCreate,
    TaskResponse
)
from app import crud

def parse_vietnamese_date(text: str) -> Optional[date]:
    """Parse common Vietnamese and standard date phrases."""
    today = date.today()
    lower = text.lower()

    if "hôm nay" in lower or "today" in lower:
        return today
    if "ngày mai" in lower or "mai" in lower or "tomorrow" in lower:
        return today + timedelta(days=1)
    if "ngày kia" in lower or "ngày mốt" in lower:
        return today + timedelta(days=2)
    if "tuần sau" in lower or "next week" in lower:
        return today + timedelta(days=7)

    # sau N ngày
    match_after_days = re.search(r"sau\s+(\d+)\s+ngày", lower)
    if match_after_days:
        days = int(match_after_days.group(1))
        return today + timedelta(days=days)

    # YYYY-MM-DD
    match_iso = re.search(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b", text)
    if match_iso:
        try:
            return date(int(match_iso.group(1)), int(match_iso.group(2)), int(match_iso.group(3)))
        except ValueError:
            pass

    # DD/MM/YYYY or DD-MM-YYYY
    match_vn = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b", text)
    if match_vn:
        try:
            return date(int(match_vn.group(3)), int(match_vn.group(2)), int(match_vn.group(1)))
        except ValueError:
            pass

    # DD/MM (current year)
    match_short = re.search(r"\b(\d{1,2})[/-](\d{1,2})\b", text)
    if match_short:
        try:
            return date(today.year, int(match_short.group(2)), int(match_short.group(1)))
        except ValueError:
            pass

    return None

def extract_priority(text: str) -> str:
    """Extract priority from text."""
    lower = text.lower()
    if any(k in lower for k in ["ưu tiên cao", "quan trọng", "gấp", "khẩn cấp", "high", "cao"]):
        return "high"
    if any(k in lower for k in ["ưu tiên thấp", "nhẹ", "thấp", "low"]):
        return "low"
    return "medium"

def generate_project_breakdown(topic: str) -> List[TaskCreate]:
    """Generate subtasks based on a given topic."""
    today = date.today()
    clean_topic = topic.replace("gợi ý", "").replace("kế hoạch", "").replace("chia nhỏ", "").strip()
    if not clean_topic:
        clean_topic = "Dự án mới"

    return [
        TaskCreate(
            title=f"Khảo sát & lập yêu cầu: {clean_topic}",
            description="Thu thập yêu cầu chi tiết, xác định mục tiêu và phạm vi thực hiện.",
            priority="high",
            due_date=today + timedelta(days=2)
        ),
        TaskCreate(
            title=f"Thiết kế kiến trúc & cơ sở dữ liệu: {clean_topic}",
            description="Thiết kế sơ đồ cơ sở dữ liệu, API contract và UI wireframes.",
            priority="high",
            due_date=today + timedelta(days=4)
        ),
        TaskCreate(
            title=f"Hiện thực hóa chức năng cốt lõi (Core features)",
            description=f"Viết mã nguồn backend và giao diện frontend cho {clean_topic}.",
            priority="medium",
            due_date=today + timedelta(days=7)
        ),
        TaskCreate(
            title=f"Kiểm thử & Tối ưu hóa (Testing & QA)",
            description="Chạy kiểm thử chức năng, sửa lỗi và kiểm tra hiệu năng hệ thống.",
            priority="medium",
            due_date=today + timedelta(days=10)
        ),
        TaskCreate(
            title=f"Triển khai & bàn giao: {clean_topic}",
            description="Đóng gói Docker, cấu hình CI/CD và triển khai lên môi trường Cloud.",
            priority="low",
            due_date=today + timedelta(days=14)
        )
    ]

class ChatbotService:
    def handle_message(self, request: ChatRequest, db: Session) -> ChatResponse:
        """Handle incoming user message with LLM or Smart Built-in NLP."""
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        openai_key = os.getenv("OPENAI_API_KEY", "").strip()

        # 1. Try Gemini LLM if configured
        if gemini_key:
            try:
                res = self._call_gemini_llm(request, db, gemini_key)
                if res:
                    return res
            except Exception as e:
                print(f"[Chatbot] Gemini call error: {e}, falling back to built-in NLP.")

        # 2. Try OpenAI LLM if configured
        if openai_key:
            try:
                res = self._call_openai_llm(request, db, openai_key)
                if res:
                    return res
            except Exception as e:
                print(f"[Chatbot] OpenAI call error: {e}, falling back to built-in NLP.")

        # 3. Smart Built-in Vietnamese NLP Engine (Instant & 100% reliable)
        return self._process_nlp(request.message, db)

    def _process_nlp(self, user_msg: str, db: Session) -> ChatResponse:
        msg = user_msg.strip()
        lower = msg.lower()

        # --- A. HELP / GUIDANCE ---
        if any(lower.startswith(k) for k in ["trợ giúp", "hướng dẫn", "bạn làm được gì", "help", "hello", "xin chào", "chào"]):
            if any(k in lower for k in ["hello", "xin chào", "chào"]) and not any(k in lower for k in ["làm được gì", "hướng dẫn", "help"]):
                reply = (
                    "👋 **Xin chào! Tôi là Trợ lý AI TaskFlow.**\n\n"
                    "Tôi có thể hỗ trợ bạn quản lý công việc cực kỳ nhanh chóng:\n"
                    "- ➕ **Tạo task mới**: *\"Tạo task Nộp báo cáo tuần sau ưu tiên cao\"*\n"
                    "- 📋 **Tra cứu**: *\"Danh sách task cần làm\"* hoặc *\"Tìm task database\"*\n"
                    "- ✅ **Hoàn thành**: *\"Hoàn thành task 1\"*\n"
                    "- 📊 **Tóm tắt**: *\"Tóm tắt tiến độ công việc\"*\n"
                    "- 💡 **Lên kế hoạch**: *\"Gợi ý các task để làm ứng dụng Mobile\"*\n\n"
                    "Bạn cần tôi hỗ trợ việc gì ngay bây giờ?"
                )
                return ChatResponse(reply=reply, action=ChatAction(type="none"), llm_used=False)

            reply = (
                "🤖 **Hướng dẫn sử dụng Trợ lý AI TaskFlow**\n\n"
                "Bạn có thể nhắn các câu lệnh tự nhiên bằng tiếng Việt hoặc tiếng Anh:\n\n"
                "1. **Tạo công việc mới:**\n"
                "   - *\"Tạo task Viết unit test trước ngày mai ưu tiên cao\"*\n"
                "   - *\"Thêm việc Chuẩn bị tài liệu thuyết trình\"*\n"
                "2. **Tra cứu & Lọc công việc:**\n"
                "   - *\"Xem các task đang chờ (pending)\"*\n"
                "   - *\"Liệt kê task ưu tiên cao\"*\n"
                "   - *\"Tìm task liên quan đến API\"*\n"
                "3. **Hoàn thành / Đổi trạng thái:**\n"
                "   - *\"Hoàn thành task 2\"* hoặc *\"Xong việc số 5\"*\n"
                "4. **Xóa công việc:**\n"
                "   - *\"Xóa task 3\"*\n"
                "5. **Tóm tắt & Báo cáo:**\n"
                "   - *\"Tóm tắt tiến độ công việc hiện tại\"*\n"
                "6. **Gợi ý phân rã dự án:**\n"
                "   - *\"Gợi ý các task cho dự án Làm website bán hàng\"*"
            )
            return ChatResponse(reply=reply, action=ChatAction(type="none"), llm_used=False)

        # --- B. SUMMARY / REPORT / STATS ---
        if any(k in lower for k in ["tóm tắt", "tiến độ", "báo cáo", "thống kê", "summary", "stats", "tình hình"]):
            all_tasks = crud.get_tasks(db)
            total = len(all_tasks)
            completed = sum(1 for t in all_tasks if t.status == "completed")
            pending = total - completed
            high_p = sum(1 for t in all_tasks if t.priority == "high" and t.status == "pending")
            today = date.today()
            overdue = sum(1 for t in all_tasks if t.due_date and t.due_date < today and t.status == "pending")

            rate = round((completed / total * 100), 1) if total > 0 else 0

            summary_data = {
                "total": total,
                "completed": completed,
                "pending": pending,
                "high_priority_pending": high_p,
                "overdue": overdue,
                "completion_rate": rate
            }

            reply = (
                f"📊 **Báo cáo Tiến độ Công việc Hiện tại**\n\n"
                f"- 📁 **Tổng số công việc:** {total}\n"
                f"- ✅ **Đã hoàn thành:** {completed} ({rate}%)\n"
                f"- ⏳ **Đang thực hiện:** {pending}\n"
                f"- 🔥 **Ưu tiên cao cần làm:** {high_p}\n"
                f"- ⚠️ **Quá hạn cần xử lý:** {overdue}\n\n"
            )

            if overdue > 0:
                reply += "⚡ *Khuyến nghị: Bạn có việc đã quá hạn, hãy ưu tiên xử lý trước!*"
            elif high_p > 0:
                reply += "🎯 *Khuyến nghị: Hãy tập trung vào các task có độ ưu tiên cao nhé!*"
            elif pending == 0 and total > 0:
                reply += "🎉 *Tuyệt vời! Tất cả công việc đã hoàn thành 100%!*"
            else:
                reply += "💪 *Tiến độ đang rất ổn định, chúc bạn làm việc hiệu quả!*"

            return ChatResponse(
                reply=reply,
                action=ChatAction(type="summary", summary_data=summary_data),
                llm_used=False
            )

        # --- C. PROJECT BREAKDOWN / SUGGESTIONS ---
        if any(k in lower for k in ["gợi ý", "lên kế hoạch", "chia nhỏ", "kế hoạch", "các bước"]):
            # Extract topic
            topic = re.sub(r"(gợi ý|lên kế hoạch|chia nhỏ|kế hoạch|các bước|cho|làm|dự án|task|cần làm)", "", lower, flags=re.IGNORECASE).strip()
            if not topic:
                topic = "Dự án mới"
            suggested = generate_project_breakdown(topic)
            reply = (
                f"💡 **Gợi ý kế hoạch phân rã công việc cho: \"{topic.title()}\"**\n\n"
                f"Tôi đã đề xuất **{len(suggested)} nhiệm vụ** từng bước cụ thể bên dưới. "
                f"Bạn có thể nhấn nút **\"Thêm tất cả vào danh sách\"** hoặc chọn thêm từng task:"
            )
            return ChatResponse(
                reply=reply,
                action=ChatAction(type="suggest_tasks", suggested_tasks=suggested),
                llm_used=False
            )

        # --- D. TOGGLE COMPLETE TASK ---
        complete_match = re.search(r"(hoàn thành|xong|đã làm xong|complete|done)\s+(task|việc|công việc|số)?\s*#?(\d+)", lower)
        if complete_match:
            task_id = int(complete_match.group(3))
            task = crud.get_task(db, task_id)
            if not task:
                return ChatResponse(
                    reply=f"❌ Không tìm thấy công việc có mã **#{task_id}**.",
                    action=ChatAction(type="none"),
                    llm_used=False
                )
            updated = crud.toggle_complete_task(db, task_id)
            st_text = "đã hoàn thành 🎉" if updated.status == "completed" else "chuyển về trạng thái đang chờ ⏳"
            task_resp = TaskResponse.model_validate(updated)
            reply = f"✅ Đã cập nhật công việc **#{task_id} - {updated.title}**: {st_text}!"
            return ChatResponse(
                reply=reply,
                action=ChatAction(type="complete_task", task=task_resp),
                llm_used=False
            )

        # --- E. DELETE TASK ---
        delete_match = re.search(r"(xóa|hủy|bỏ|delete|remove)\s+(task|việc|công việc|số)?\s*#?(\d+)", lower)
        if delete_match:
            task_id = int(delete_match.group(3))
            task = crud.get_task(db, task_id)
            if not task:
                return ChatResponse(
                    reply=f"❌ Không tìm thấy công việc có mã **#{task_id}** để xóa.",
                    action=ChatAction(type="none"),
                    llm_used=False
                )
            title = task.title
            crud.delete_task(db, task_id)
            return ChatResponse(
                reply=f"🗑️ Đã xóa công việc **#{task_id} (\"{title}\")** thành công.",
                action=ChatAction(type="delete_task"),
                llm_used=False
            )

        # --- F. LIST / SEARCH TASKS ---
        if any(k in lower for k in ["danh sách", "liệt kê", "có task nào", "xem task", "xem việc", "list task", "tìm task", "tìm việc"]):
            filter_status = None
            if "pending" in lower or "chưa xong" in lower or "đang chờ" in lower or "cần làm" in lower:
                filter_status = "pending"
            elif "hoàn thành" in lower or "completed" in lower or "đã xong" in lower:
                filter_status = "completed"

            filter_priority = None
            if "cao" in lower or "high" in lower:
                filter_priority = "high"
            elif "thấp" in lower or "low" in lower:
                filter_priority = "low"

            # Search keyword
            search_term = None
            search_match = re.search(r"(tìm task|tìm việc|tìm kiếm)\s+(?:liên quan đến\s+|về\s+)?(.+)", lower)
            if search_match:
                search_term = search_match.group(2).strip()

            tasks = crud.get_tasks(db, status=filter_status, priority=filter_priority, search=search_term)
            tasks_resp = [TaskResponse.model_validate(t) for t in tasks]

            if not tasks:
                return ChatResponse(
                    reply="📭 Không tìm thấy công việc nào phù hợp với yêu cầu tìm kiếm của bạn.",
                    action=ChatAction(type="list_tasks", tasks=[]),
                    llm_used=False
                )

            reply = f"📋 **Tìm thấy {len(tasks)} công việc:**\n\n"
            for t in tasks[:8]:
                st_icon = "✅" if t.status == "completed" else "⏳"
                p_badge = {"high": "🔥 Cao", "medium": "⚡ Trung bình", "low": "🌱 Thấp"}.get(t.priority, t.priority)
                due_info = f" • Hạn: {t.due_date.strftime('%d/%m/%Y')}" if t.due_date else ""
                reply += f"- **#{t.id}** {st_icon} {t.title} `[{p_badge}]`{due_info}\n"

            if len(tasks) > 8:
                reply += f"\n*... và còn {len(tasks) - 8} công việc khác.*"

            return ChatResponse(
                reply=reply,
                action=ChatAction(type="list_tasks", tasks=tasks_resp),
                llm_used=False
            )

        # --- G. CREATE TASK ---
        create_triggers = ["tạo task", "thêm task", "tạo việc", "thêm việc", "tạo công việc", "thêm công việc", "add task", "new task", "tạo"]
        is_create = any(lower.startswith(trigger) or f" {trigger} " in lower for trigger in create_triggers)

        if is_create or (len(msg) > 3 and not msg.endswith("?")):
            # Extract content after trigger
            task_text = msg
            for trigger in create_triggers:
                if trigger in lower:
                    idx = lower.find(trigger) + len(trigger)
                    task_text = msg[idx:].strip(" :-\t")
                    break

            # If task_text is too short or is a generic query
            if len(task_text) < 2:
                task_text = msg

            # Extract priority and due date
            priority = extract_priority(msg)
            due_date = parse_vietnamese_date(msg)

            # Clean title
            cleaned_title = task_text
            # remove priority words from title
            cleaned_title = re.sub(
                r"(ưu tiên cao|ưu tiên thấp|ưu tiên trung bình|mức độ cao|mức độ thấp|mức độ trung bình|quan trọng|gấp|khẩn cấp|high priority|low priority)",
                "",
                cleaned_title,
                flags=re.IGNORECASE
            )
            # remove date phrases from title
            cleaned_title = re.sub(
                r"(trước ngày mai|ngày mai|hôm nay|ngày mốt|ngày kia|tuần sau|sau \d+ ngày|\d{4}-\d{1,2}-\d{1,2}|\d{1,2}[/-]\d{1,2}[/-]\d{4})",
                "",
                cleaned_title,
                flags=re.IGNORECASE
            )
            cleaned_title = re.sub(r"(trước|hạn|due date|hạn chót)?:?\s*$", "", cleaned_title).strip(" ,.-:")

            if not cleaned_title:
                cleaned_title = task_text.strip()

            new_task_in = TaskCreate(
                title=cleaned_title,
                description=f"Tạo tự động bởi AI Assistant từ yêu cầu: \"{msg}\"",
                priority=priority,
                status="pending",
                due_date=due_date
            )
            created_task = crud.create_task(db, new_task_in)
            task_resp = TaskResponse.model_validate(created_task)

            p_badge = {"high": "🔥 Cao", "medium": "⚡ Trung bình", "low": "🌱 Thấp"}.get(priority, priority)
            due_str = due_date.strftime("%d/%m/%Y") if due_date else "Chưa đặt"

            reply = (
                f"✨ **Đã tạo thành công công việc mới!**\n\n"
                f"- 📌 **Tiêu đề:** {created_task.title}\n"
                f"- 🏷️ **Mã ID:** #{created_task.id}\n"
                f"- 🎯 **Mức ưu tiên:** {p_badge}\n"
                f"- 📅 **Hạn hoàn thành:** {due_str}\n\n"
                f"Công việc đã xuất hiện ngay trên danh sách của bạn!"
            )

            return ChatResponse(
                reply=reply,
                action=ChatAction(type="create_task", task=task_resp),
                llm_used=False
            )

        # Fallback default friendly reply
        return ChatResponse(
            reply=(
                "🤔 Tôi chưa hiểu rõ yêu cầu của bạn.\n\n"
                "Bạn có thể thử các mẫu câu như:\n"
                "- *\"Tạo task [Nội dung công việc] trước [ngày] ưu tiên [cao/thấp]\"*\n"
                "- *\"Danh sách task cần làm\"*\n"
                "- *\"Hoàn thành task [ID]\"*\n"
                "- *\"Tóm tắt tiến độ công việc\"*\n"
                "- *\"Gợi ý các bước cho dự án [Tên dự án]\"*"
            ),
            action=ChatAction(type="none"),
            llm_used=False
        )

    def _call_gemini_llm(self, request: ChatRequest, db: Session, api_key: str) -> Optional[ChatResponse]:
        """Call Google Gemini API with smart tool fallback."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={api_key}"

        all_tasks = crud.get_tasks(db)
        tasks_context = [
            {"id": t.id, "title": t.title, "status": t.status, "priority": t.priority, "due_date": str(t.due_date) if t.due_date else None}
            for t in all_tasks[:25]
        ]

        system_instruction = (
            "Bạn là trợ lý AI thông minh cho ứng dụng quản lý công việc TaskFlow.\n"
            "Nhiệm vụ của bạn là hỗ trợ người dùng tạo task, tra cứu task, đánh dấu hoàn thành, xóa task hoặc tóm tắt tiến độ.\n"
            f"Dưới đây là danh sách task hiện tại trong cơ sở dữ liệu:\n{json.dumps(tasks_context, ensure_ascii=False)}\n"
            "Hãy trả lời bằng tiếng Việt thân thiện, rõ ràng, định dạng markdown đẹp mắt."
        )

        contents = []
        for h in request.history[-6:]:
            role = "user" if h.role == "user" else "model"
            contents.append({"role": role, "parts": [{"text": h.content}]})

        contents.append({"role": "user", "parts": [{"text": request.message}]})

        payload = {
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "contents": contents,
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 1000
            }
        }

        with httpx.Client(timeout=3.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code != 200:
                return None
            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return None
            reply_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")

            # Check if user message is actually a task modification, if so we execute it in DB via NLP
            nlp_res = self._process_nlp(request.message, db)
            if nlp_res.action and nlp_res.action.type != "none":
                return ChatResponse(
                    reply=reply_text,
                    action=nlp_res.action,
                    llm_used=True,
                    provider="Google Gemini"
                )

            return ChatResponse(
                reply=reply_text,
                action=ChatAction(type="none"),
                llm_used=True,
                provider="Google Gemini"
            )

    def _call_openai_llm(self, request: ChatRequest, db: Session, api_key: str) -> Optional[ChatResponse]:
        """Call OpenAI-compatible Chat API."""
        url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1") + "/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        all_tasks = crud.get_tasks(db)
        tasks_context = [
            {"id": t.id, "title": t.title, "status": t.status, "priority": t.priority, "due_date": str(t.due_date) if t.due_date else None}
            for t in all_tasks[:25]
        ]

        messages = [
            {
                "role": "system",
                "content": (
                    "Bạn là trợ lý AI của TaskFlow. Nhiệm vụ là hỗ trợ người dùng quản lý công việc.\n"
                    f"Dữ liệu task hiện có:\n{json.dumps(tasks_context, ensure_ascii=False)}"
                )
            }
        ]
        for h in request.history[-6:]:
            messages.append({"role": h.role, "content": h.content})
        messages.append({"role": "user", "content": request.message})

        payload = {
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "messages": messages,
            "temperature": 0.4,
            "max_tokens": 800
        }

        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                return None
            data = resp.json()
            reply_text = data["choices"][0]["message"]["content"]

            # If user made an action, execute it via NLP
            nlp_res = self._process_nlp(request.message, db)
            action = nlp_res.action if nlp_res.action and nlp_res.action.type != "none" else ChatAction(type="none")

            return ChatResponse(
                reply=reply_text,
                action=action,
                llm_used=True,
                provider="OpenAI"
            )

chatbot_service = ChatbotService()
