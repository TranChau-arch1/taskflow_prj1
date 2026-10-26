import React from "react";

export default function TaskItem({
  task,
  onToggleComplete,
  onEdit,
  onDelete
}) {
  const isCompleted = task.status === "completed";

  // Check if overdue
  let isOverdue = false;
  let formattedDueDate = null;
  if (task.due_date) {
    const today = new Date().toISOString().split("T")[0];
    if (task.due_date < today && !isCompleted) {
      isOverdue = true;
    }
    const [year, month, day] = task.due_date.split("-");
    formattedDueDate = `${day}/${month}/${year}`;
  }

  const priorityLabels = {
    high: { text: "Ưu tiên cao", class: "badge-high" },
    medium: { text: "Trung bình", class: "badge-medium" },
    low: { text: "Thấp", class: "badge-low" },
  };

  const currentPriority = priorityLabels[task.priority] || priorityLabels.medium;

  return (
    <div className={`task-card ${isCompleted ? "task-completed" : ""}`}>
      <div className="task-main">
        <label className="checkbox-container" title={isCompleted ? "Đánh dấu chưa hoàn thành" : "Đánh dấu đã hoàn thành"}>
          <input
            type="checkbox"
            checked={isCompleted}
            onChange={() => onToggleComplete(task.id)}
          />
          <span className="checkmark"></span>
        </label>

        <div className="task-content">
          <div className="task-header-row">
            <h3 className="task-title">{task.title}</h3>
            <span className={`priority-badge ${currentPriority.class}`}>
              {currentPriority.text}
            </span>
          </div>

          {task.description && (
            <p className="task-description">{task.description}</p>
          )}

          <div className="task-meta">
            {formattedDueDate && (
              <span className={`meta-pill ${isOverdue ? "meta-overdue" : ""}`}>
                📅 {formattedDueDate} {isOverdue && "(Quá hạn)"}
              </span>
            )}
            <span className="meta-pill meta-date">
              Tạo: {new Date(task.created_at).toLocaleDateString("vi-VN")}
            </span>
          </div>
        </div>
      </div>

      <div className="task-actions">
        <button
          className="btn-action btn-edit"
          onClick={() => onEdit(task)}
          title="Sửa công việc"
        >
          ✏️ Sửa
        </button>
        <button
          className="btn-action btn-delete"
          onClick={() => onDelete(task.id, task.title)}
          title="Xóa công việc"
        >
          🗑️ Xóa
        </button>
      </div>
    </div>
  );
}
