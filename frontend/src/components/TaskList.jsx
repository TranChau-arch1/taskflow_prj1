import React from "react";
import TaskItem from "./TaskItem";

export default function TaskList({
  tasks,
  loading,
  onToggleComplete,
  onEdit,
  onDelete,
  onOpenCreateModal
}) {
  if (loading) {
    return (
      <div className="task-loading-state">
        <div className="spinner"></div>
        <p>Đang tải dữ liệu công việc...</p>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">📋</div>
        <h3>Không tìm thấy công việc nào</h3>
        <p>Thử đổi bộ lọc hoặc tạo một công việc mới để bắt đầu theo dõi.</p>
        <button className="btn btn-primary btn-sm" onClick={onOpenCreateModal}>
          + Thêm công việc ngay
        </button>
      </div>
    );
  }

  return (
    <div className="tasks-wrapper">
      <div className="tasks-count-bar">
        <span>Hiển thị <strong>{tasks.length}</strong> công việc</span>
      </div>
      <div className="task-list">
        {tasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            onToggleComplete={onToggleComplete}
            onEdit={onEdit}
            onDelete={onDelete}
          />
        ))}
      </div>
    </div>
  );
}
