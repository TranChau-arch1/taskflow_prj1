import React, { useState, useEffect } from "react";

export default function TaskModal({
  isOpen,
  onClose,
  onSubmit,
  initialData = null,
  isSubmitting = false
}) {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    priority: "medium",
    due_date: "",
    status: "pending"
  });

  const [validationError, setValidationError] = useState("");

  useEffect(() => {
    if (initialData) {
      setFormData({
        title: initialData.title || "",
        description: initialData.description || "",
        priority: initialData.priority || "medium",
        due_date: initialData.due_date || "",
        status: initialData.status || "pending"
      });
    } else {
      setFormData({
        title: "",
        description: "",
        priority: "medium",
        due_date: "",
        status: "pending"
      });
    }
    setValidationError("");
  }, [initialData, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.title.trim()) {
      setValidationError("Vui lòng nhập tiêu đề công việc.");
      return;
    }

    const payload = {
      title: formData.title.trim(),
      description: formData.description.trim() || null,
      priority: formData.priority,
      status: formData.status,
      due_date: formData.due_date || null
    };

    onSubmit(payload);
  };

  const isEditing = Boolean(initialData && initialData.id);

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{isEditing ? "Chỉnh sửa công việc" : "Thêm công việc mới"}</h2>
          <button className="modal-close-btn" onClick={onClose}>✕</button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          {validationError && (
            <div className="form-error-alert">{validationError}</div>
          )}

          <div className="form-group">
            <label htmlFor="task-title">Tiêu đề công việc <span className="required">*</span></label>
            <input
              id="task-title"
              type="text"
              className="form-control"
              placeholder="Ví dụ: Thiết kế giao diện website..."
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="task-desc">Mô tả chi tiết</label>
            <textarea
              id="task-desc"
              rows="3"
              className="form-control"
              placeholder="Ghi chú thêm thông tin hoặc các bước cần làm..."
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
          </div>

          <div className="form-row">
            <div className="form-group col">
              <label htmlFor="task-priority">Mức ưu tiên</label>
              <select
                id="task-priority"
                className="form-control"
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
              >
                <option value="low">Thấp (Low)</option>
                <option value="medium">Trung bình (Medium)</option>
                <option value="high">Cao (High)</option>
              </select>
            </div>

            <div className="form-group col">
              <label htmlFor="task-due-date">Hạn hoàn thành</label>
              <input
                id="task-due-date"
                type="date"
                className="form-control"
                value={formData.due_date}
                onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
              />
            </div>
          </div>

          {isEditing && (
            <div className="form-group">
              <label htmlFor="task-status">Trạng thái</label>
              <select
                id="task-status"
                className="form-control"
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              >
                <option value="pending">Đang chờ (Pending)</option>
                <option value="completed">Đã hoàn thành (Completed)</option>
              </select>
            </div>
          )}

          <div className="modal-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Hủy bỏ
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Đang lưu..." : isEditing ? "Cập nhật" : "Tạo công việc"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
