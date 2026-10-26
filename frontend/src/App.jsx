import React, { useState, useEffect, useCallback } from "react";
import TaskHeader from "./components/TaskHeader";
import TaskStats from "./components/TaskStats";
import TaskFilters from "./components/TaskFilters";
import TaskList from "./components/TaskList";
import TaskModal from "./components/TaskModal";
import { taskApi } from "./services/taskApi";

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [allTasksForStats, setAllTasksForStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isBackendOnline, setIsBackendOnline] = useState(false);

  // Filters state
  const [filters, setFilters] = useState({
    status: "all",
    priority: "all",
    search: ""
  });

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Notification toast
  const [toast, setToast] = useState(null);

  const showToast = (message, type = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  };

  // Fetch all tasks for stats counter
  const fetchStatsTasks = useCallback(async () => {
    try {
      const data = await taskApi.getTasks({});
      setAllTasksForStats(data);
    } catch {
      // stats error ignored
    }
  }, []);

  // Fetch tasks with current filters
  const fetchTasks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await taskApi.getTasks(filters);
      setTasks(data);
      setIsBackendOnline(true);
    } catch (err) {
      console.error(err);
      setError(err.message || "Không thể tải danh sách công việc");
      setIsBackendOnline(false);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  // Initial load & health check
  useEffect(() => {
    const checkServer = async () => {
      try {
        await taskApi.checkHealth();
        setIsBackendOnline(true);
      } catch {
        setIsBackendOnline(false);
      }
    };
    checkServer();
    fetchTasks();
    fetchStatsTasks();
  }, [fetchTasks, fetchStatsTasks]);

  // Handle filter changes
  const handleFilterChange = (newFilters) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  };

  const handleResetFilters = () => {
    setFilters({ status: "all", priority: "all", search: "" });
  };

  const hasActiveFilters =
    filters.status !== "all" || filters.priority !== "all" || filters.search !== "";

  // Open Modal
  const handleOpenCreateModal = () => {
    setEditingTask(null);
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (task) => {
    setEditingTask(task);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingTask(null);
  };

  // Handle Submit (Create or Update)
  const handleSubmitTask = async (formData) => {
    setIsSubmitting(true);
    try {
      if (editingTask) {
        await taskApi.updateTask(editingTask.id, formData);
        showToast("Đã cập nhật công việc thành công!");
      } else {
        await taskApi.createTask(formData);
        showToast("Đã tạo công việc mới thành công!");
      }
      handleCloseModal();
      await fetchTasks();
      await fetchStatsTasks();
    } catch (err) {
      alert("Lỗi: " + (err.message || "Không thể lưu công việc"));
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle Toggle Complete
  const handleToggleComplete = async (taskId) => {
    try {
      const updated = await taskApi.toggleComplete(taskId);
      showToast(
        updated.status === "completed"
          ? "Đã đánh dấu hoàn thành! 🎉"
          : "Đã chuyển về trạng thái đang chờ."
      );
      // Optimistic update
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, status: updated.status } : t))
      );
      setAllTasksForStats((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, status: updated.status } : t))
      );
      // Refetch if status filter is active
      if (filters.status !== "all") {
        fetchTasks();
      }
    } catch (err) {
      alert("Lỗi khi đổi trạng thái: " + err.message);
    }
  };

  // Handle Delete Task
  const handleDeleteTask = async (taskId, taskTitle) => {
    if (!window.confirm(`Bạn có chắc muốn xóa công việc "${taskTitle}"?`)) {
      return;
    }
    try {
      await taskApi.deleteTask(taskId);
      showToast("Đã xóa công việc.");
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
      setAllTasksForStats((prev) => prev.filter((t) => t.id !== taskId));
    } catch (err) {
      alert("Lỗi khi xóa: " + err.message);
    }
  };

  return (
    <div className="app-container">
      {/* Toast Notification */}
      {toast && (
        <div className={`toast-notification toast-${toast.type}`}>
          {toast.message}
        </div>
      )}

      {/* Header */}
      <TaskHeader
        onOpenCreateModal={handleOpenCreateModal}
        isBackendOnline={isBackendOnline}
        apiBaseUrl={taskApi.getBaseUrl()}
      />

      <main className="main-content">
        {/* Statistics Bar */}
        <TaskStats tasks={allTasksForStats} />

        {/* Global Error Banner */}
        {error && (
          <div className="error-banner">
            <div className="error-content">
              <strong>⚠️ Lỗi kết nối:</strong> {error}
            </div>
            <button className="btn btn-secondary btn-sm" onClick={fetchTasks}>
              Thử lại
            </button>
          </div>
        )}

        {/* Filters */}
        <TaskFilters
          filters={filters}
          onChangeFilters={handleFilterChange}
          onResetFilters={handleResetFilters}
          hasActiveFilters={hasActiveFilters}
        />

        {/* Task List */}
        <TaskList
          tasks={tasks}
          loading={loading}
          onToggleComplete={handleToggleComplete}
          onEdit={handleOpenEditModal}
          onDelete={handleDeleteTask}
          onOpenCreateModal={handleOpenCreateModal}
        />
      </main>

      {/* Create / Edit Modal */}
      <TaskModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSubmit={handleSubmitTask}
        initialData={editingTask}
        isSubmitting={isSubmitting}
      />

      <footer className="app-footer">
        <p>
          TaskFlow MVP • Phát triển với <strong>React + Vite + FastAPI + PostgreSQL</strong>
        </p>
      </footer>
    </div>
  );
}
