# 🚀 TaskFlow — Website Quản Lý Công Việc (Task Manager)

> **TaskFlow** là ứng dụng web quản lý công việc hiện đại với kiến trúc tách biệt Frontend & Backend, lưu trữ cơ sở dữ liệu trên cloud và sẵn sàng deploy lên Internet theo kế hoạch 3 ngày.

---

## 📑 Mục Lục
1. [Kiến Trúc & Công Nghệ](#1-kiến-trúc--công-nghệ)
2. [Cấu Trúc Thư Mục](#2-cấu-trúc-thư-mục)
3. [Hướng Dẫn Chạy Cục Bộ (Local)](#3-hướng-dẫn-chạy-cục-bộ-local)
4. [Tài Liệu REST API](#4-tài-liệu-rest-api)
5. [Hướng Dẫn Deploy Lên Internet (Ngày 3)](#5-hướng-dẫn-deploy-lên-internet-ngày-3)
   - [Bước 1: Cloud Database trên Neon](#bước-1-khởi-tạo-postgresql-trên-neon)
   - [Bước 2: Deploy Backend lên Render](#bước-2-deploy-backend-lên-render)
   - [Bước 3: Deploy Frontend lên Vercel](#bước-3-deploy-frontend-lên-vercel)
   - [Bước 4: Cấu hình CORS](#bước-4-kết-nối-và-cấu-hình-cors)
6. [Checklist Nghiệm Thu](#6-checklist-nghiệm-thu-99)
7. [Khắc Phục Lỗi Thường Gặp (Troubleshooting)](#7-khắc-phục-lỗi-thường-gặp)

---

## 1. Kiến Trúc & Công Nghệ

```
[ Người dùng ]
      │
      ▼ (HTTPS)
[ Frontend (React + Vite) ]  ─── Hosted on Vercel
      │
      ▼ REST API (fetch + JSON)
[ Backend (FastAPI + SQLAlchemy) ] ─── Hosted on Render
      │
      ▼ Connection Pool (SSL)
[ Database (PostgreSQL) ]  ─── Hosted on Neon.tech
```

| Thành phần | Công nghệ | Dịch vụ Cloud |
| :--- | :--- | :--- |
| **Frontend** | React 18, Vite, Vanilla CSS hiện đại, Responsive UI | **Vercel** |
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy, Pydantic v2 | **Render** |
| **Database** | PostgreSQL (Production) / SQLite (Local Dev) | **Neon.tech** |
| **Quản lý mã nguồn** | Git & GitHub Monorepo | **GitHub** |

---

## 2. Cấu Trúc Thư Mục

Dự án được tổ chức theo mô hình **Monorepo** gọn gàng:

```text
ai-deployment-lab/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TaskHeader.jsx     # Header, trạng thái kết nối API & nút thêm
│   │   │   ├── TaskStats.jsx      # Thẻ thống kê: Tổng, Chờ, Hoàn thành, Ưu tiên
│   │   │   ├── TaskFilters.jsx    # Thanh tìm kiếm, lọc status, lọc priority
│   │   │   ├── TaskItem.jsx       # Từng thẻ công việc, nút xóa, sửa, checkbox
│   │   │   ├── TaskList.jsx       # Danh sách, trạng thái trống & loading
│   │   │   └── TaskModal.jsx      # Modal pop-up thêm mới & chỉnh sửa task
│   │   ├── services/
│   │   │   └── taskApi.js         # Toàn bộ hàm gọi API bằng fetch()
│   │   ├── App.jsx                # Quản lý state tập trung & xử lý CRUD
│   │   ├── main.jsx               # Render React DOM
│   │   └── index.css              # Giao diện Dark mode hiện đại, glassmorphism
│   ├── index.html
│   ├── package.json
│   ├── vercel.json                # Định tuyến SPA cho Vercel
│   └── .env.example
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── database.py            # Kết nối SQLAlchemy (hỗ trợ cả SQLite & Postgres)
│   │   ├── models.py              # Định nghĩa bảng 'tasks'
│   │   ├── schemas.py             # Validate dữ liệu request/response với Pydantic
│   │   ├── crud.py                # Truy vấn cơ sở dữ liệu (CRUD logic)
│   │   ├── routers/
│   │   │   └── tasks.py           # Khai báo các REST endpoint /api/tasks
│   │   └── main.py                # Khởi tạo FastAPI, CORS & route /health
│   ├── Dockerfile                 # Dựng container cho Render hoặc VPS
│   ├── requirements.txt           # Danh sách thư viện Python
│   ├── test_api.py                # Script kiểm thử tự động API
│   └── .env.example
├── .gitignore
└── README.md
```

---

## 3. Hướng Dẫn Chạy Cục Bộ (Local)

### 3.1. Khởi chạy Backend

1. Mở Terminal tại thư mục `backend`:
   ```bash
   cd backend
   ```
2. Tạo và kích hoạt môi trường ảo Python:
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
3. Cài đặt thư viện:
   ```bash
   pip install -r requirements.txt
   ```
4. Khởi động server FastAPI:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - Server chạy tại: `http://127.0.0.1:8000`
   - Tài liệu tương tác Swagger UI: `http://127.0.0.1:8000/docs`
   - Kiểm tra sức khỏe: `http://127.0.0.1:8000/health`

*(Mặc định khi chạy local, nếu không có biến `DATABASE_URL`, hệ thống sẽ tự động tạo và lưu trữ trên file SQLite `taskflow.db` rất nhanh chóng).*

---

### 3.2. Khởi chạy Frontend

1. Mở một cửa sổ Terminal khác tại thư mục `frontend`:
   ```bash
   cd frontend
   ```
2. Cài đặt các gói thư viện Node:
   ```bash
   npm install
   ```
3. Tạo file cấu hình môi trường `.env`:
   ```bash
   # Nội dung file frontend/.env
   VITE_API_BASE_URL=http://localhost:8000
   ```
4. Khởi chạy dev server:
   ```bash
   npm run dev
   ```
   - Mở trình duyệt tại: `http://localhost:5173`

---

## 4. Tài Liệu REST API

| Method | Endpoint | Mô tả | Query Params / Body |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Kiểm tra trạng thái server & ping database | Không |
| `GET` | `/api/tasks` | Lấy danh sách công việc | `?status=pending&priority=high&search=abc` |
| `GET` | `/api/tasks/{id}` | Lấy chi tiết một task theo ID | ID (int) |
| `POST` | `/api/tasks` | Tạo mới một công việc | Body JSON (`title`, `description`, `priority`, `due_date`) |
| `PUT` | `/api/tasks/{id}` | Cập nhật thông tin công việc | Body JSON cập nhật |
| `PATCH`| `/api/tasks/{id}/complete` | Đổi trạng thái `pending` ↔ `completed` | ID (int) |
| `DELETE`| `/api/tasks/{id}` | Xóa vĩnh viễn một công việc | ID (int) |

---

## 5. Hướng Dẫn Deploy Lên Internet (Ngày 3)

### Bước 1: Khởi tạo PostgreSQL trên Neon
1. Đăng ký tài khoản miễn phí tại **[Neon.tech](https://neon.tech)**.
2. Tạo một Project mới (đặt tên: `taskflow-db`).
3. Sau khi tạo xong, tại trang **Dashboard**, sao chép chuỗi kết nối **Connection String**:
   ```
   postgresql://alex:Abc123xyz@ep-cool-cloud-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

---

### Bước 2: Deploy Backend lên Render
1. Đẩy code dự án lên kho chứa GitHub cá nhân của bạn.
2. Đăng nhập vào **[Render.com](https://render.com)**.
3. Nhấp chọn **New +** ➔ **Web Service**.
4. Kết nối tới repository GitHub của bạn và điền cấu hình:
   - **Name**: `taskflow-backend`
   - **Region**: Singapore (hoặc Oregon / Frankfurt)
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Tại mục **Environment Variables**, thêm 2 biến:
   - `DATABASE_URL`: *(Dán chuỗi Connection String từ Neon đã copy ở Bước 1)*
   - `ALLOWED_ORIGINS`: `*` *(Tạm thời để `*`, sau khi có URL Vercel sẽ cập nhật lại)*
6. Bấm **Deploy Web Service**.
7. Sau khi build xong, copy URL backend của bạn (ví dụ: `https://taskflow-backend.onrender.com`).
   - Kiểm tra đường dẫn: `https://taskflow-backend.onrender.com/health` (phải trả về `{"status":"online","database":"healthy"}`).

---

### Bước 3: Deploy Frontend lên Vercel
1. Đăng nhập vào **[Vercel.com](https://vercel.com)**.
2. Nhấp chọn **Add New...** ➔ **Project**.
3. Chọn repository GitHub vừa tạo.
4. Cấu hình cài đặt:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Nhấp chọn `frontend`
5. Tại mục **Environment Variables**, thêm:
   - **Key**: `VITE_API_BASE_URL`
   - **Value**: `https://taskflow-backend.onrender.com` *(URL Render bạn vừa tạo ở Bước 2)*
6. Nhấp **Deploy**. Vercel sẽ build và cung cấp cho bạn một URL công khai (ví dụ: `https://taskflow-client.vercel.app`).

---

### Bước 4: Kết nối và Cấu hình CORS
1. Quay lại trang **Render** ➔ Web Service Backend ➔ Tab **Environment**.
2. Đổi biến `ALLOWED_ORIGINS` từ `*` thành URL Vercel của bạn:
   ```
   ALLOWED_ORIGINS=https://taskflow-client.vercel.app,http://localhost:5173
   ```
3. Nhấp **Save Changes** để backend reload.
4. Mở website Vercel trên trình duyệt và thử tạo task, đổi trạng thái, lọc dữ liệu!

---

## 6. Checklist Nghiệm Thu (9/9)

- [x] **1. Giao diện mở được bằng URL công khai** (Vercel)
- [x] **2. Thêm công việc mới thành công**, dữ liệu cập nhật tức thì
- [x] **3. Chỉnh sửa và xóa công việc thành công**
- [x] **4. Đổi trạng thái (Pending ↔ Completed)** và bộ lọc hoạt động chuẩn xác
- [x] **5. Dữ liệu vẫn được giữ nguyên sau khi F5 tải lại**
- [x] **6. Backend kết nối thành công với PostgreSQL Cloud (Neon)**
- [x] **7. Không bị lỗi chặn CORS** khi frontend gọi tới backend
- [x] **8. Mã nguồn có README đầy đủ**, cấu trúc chuẩn RESTful API
- [x] **9. File `.env` và mật khẩu bí mật không bị lộ lên GitHub**

---

## 7. Khắc Phục Lỗi Thường Gặp

> **Q: Render báo lỗi `driver not found` khi kết nối PostgreSQL?**
> A: File `app/database.py` trong dự án đã được tích hợp tự động thay thế chuỗi kết nối từ `postgres://` sang `postgresql+psycopg://` để tương thích hoàn toàn với thư viện `psycopg` mới nhất.

> **Q: Lần đầu mở web trên Render mất 30-50 giây mới hiện task?**
> A: Gói Free của Render sẽ chuyển server sang trạng thái ngủ (Sleep) khi không có lượt truy cập sau 15 phút. Khi có request đầu tiên, server mất khoảng 30s để thức dậy (Cold Start). Bạn có thể nhìn vào đèn tín hiệu *API Online* ở góc header để biết khi nào server đã sẵn sàng.

> **Q: Gặp lỗi CORS `Access-Control-Allow-Origin` trên trình duyệt?**
> A: Đảm bảo URL trong biến `ALLOWED_ORIGINS` trên Render khớp chính xác với URL trên thanh địa chỉ của Vercel (không thừa dấu `/` ở cuối).
