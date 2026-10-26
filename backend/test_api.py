import sys
import io

# Ensure UTF-8 output encoding for Windows terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_endpoints():
    # 1. Health check
    res = client.get("/health")
    print("GET /health ->", res.status_code, res.json())
    assert res.status_code == 200

    # 2. Create task
    payload = {
        "title": "Hoàn thành website TaskFlow",
        "description": "Kiểm thử và deploy ứng dụng MVP",
        "status": "pending",
        "priority": "high",
        "due_date": "2026-10-29"
    }
    res = client.post("/api/tasks", json=payload)
    print("POST /api/tasks ->", res.status_code, res.json())
    assert res.status_code == 201
    task_id = res.json()["id"]

    # 3. List tasks
    res = client.get("/api/tasks")
    print("GET /api/tasks -> count:", len(res.json()))
    assert len(res.json()) >= 1

    # 4. Toggle complete
    res = client.patch(f"/api/tasks/{task_id}/complete")
    print("PATCH /complete -> status:", res.json()["status"])
    assert res.json()["status"] == "completed"

    print("ALL TESTS PASSED! 🎉")

if __name__ == "__main__":
    test_endpoints()
