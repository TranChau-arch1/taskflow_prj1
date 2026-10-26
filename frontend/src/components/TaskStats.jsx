import React from "react";

export default function TaskStats({ tasks = [] }) {
  const total = tasks.length;
  const completed = tasks.filter((t) => t.status === "completed").length;
  const pending = total - completed;
  const highPriority = tasks.filter((t) => t.priority === "high" && t.status !== "completed").length;
  const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0;

  return (
    <div className="stats-grid">
      <div className="stat-card">
        <div className="stat-label">Tổng công việc</div>
        <div className="stat-value">{total}</div>
        <div className="stat-desc">Tất cả mục đã tạo</div>
      </div>

      <div className="stat-card stat-pending">
        <div className="stat-label">Cần thực hiện</div>
        <div className="stat-value">{pending}</div>
        <div className="stat-desc">Đang chờ hoàn tất</div>
      </div>

      <div className="stat-card stat-completed">
        <div className="stat-label">Đã hoàn thành</div>
        <div className="stat-value">{completed}</div>
        <div className="stat-desc">{completionRate}% tiến độ</div>
      </div>

      <div className="stat-card stat-high">
        <div className="stat-label">Ưu tiên cao</div>
        <div className="stat-value">{highPriority}</div>
        <div className="stat-desc">Cần tập trung giải quyết</div>
      </div>
    </div>
  );
}
