import React from "react";

export default function TaskHeader({ onOpenCreateModal, isBackendOnline, apiBaseUrl }) {
  return (
    <header className="app-header">
      <div className="header-brand">
        <div className="logo-badge">
          <span className="logo-icon">✓</span>
        </div>
        <div>
          <h1 className="brand-title">TaskFlow</h1>
          <p className="brand-subtitle">Hệ thống quản lý công việc cá nhân thông minh</p>
        </div>
      </div>

      <div className="header-actions">
        <div className={`status-pill ${isBackendOnline ? "online" : "offline"}`} title={`API: ${apiBaseUrl}`}>
          <span className="status-dot"></span>
          <span>{isBackendOnline ? "API Online" : "Mất kết nối API"}</span>
        </div>

        <button
          id="btn-create-task"
          className="btn btn-primary"
          onClick={onOpenCreateModal}
        >
          <span className="btn-icon">+</span> Thêm công việc
        </button>
      </div>
    </header>
  );
}
