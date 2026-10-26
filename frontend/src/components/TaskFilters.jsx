import React from "react";

export default function TaskFilters({
  filters,
  onChangeFilters,
  onResetFilters,
  hasActiveFilters
}) {
  return (
    <div className="filters-container">
      <div className="search-box">
        <span className="search-icon">🔍</span>
        <input
          id="task-search-input"
          type="text"
          placeholder="Tìm kiếm theo tiêu đề hoặc nội dung..."
          value={filters.search}
          onChange={(e) => onChangeFilters({ search: e.target.value })}
        />
        {filters.search && (
          <button
            className="clear-search-btn"
            onClick={() => onChangeFilters({ search: "" })}
            title="Xóa tìm kiếm"
          >
            ✕
          </button>
        )}
      </div>

      <div className="filters-row">
        <div className="status-tabs">
          <button
            className={`tab-btn ${filters.status === "all" ? "active" : ""}`}
            onClick={() => onChangeFilters({ status: "all" })}
          >
            Tất cả
          </button>
          <button
            className={`tab-btn ${filters.status === "pending" ? "active" : ""}`}
            onClick={() => onChangeFilters({ status: "pending" })}
          >
            Đang chờ
          </button>
          <button
            className={`tab-btn ${filters.status === "completed" ? "active" : ""}`}
            onClick={() => onChangeFilters({ status: "completed" })}
          >
            Đã xong
          </button>
        </div>

        <div className="priority-select-wrapper">
          <label htmlFor="priority-filter" className="filter-label">Mức ưu tiên:</label>
          <select
            id="priority-filter"
            className="select-input"
            value={filters.priority}
            onChange={(e) => onChangeFilters({ priority: e.target.value })}
          >
            <option value="all">Tất cả mức độ</option>
            <option value="high">Cao (High)</option>
            <option value="medium">Trung bình (Medium)</option>
            <option value="low">Thấp (Low)</option>
          </select>
        </div>

        {hasActiveFilters && (
          <button
            className="btn btn-secondary btn-sm"
            onClick={onResetFilters}
            title="Đặt lại bộ lọc"
          >
            Đặt lại
          </button>
        )}
      </div>
    </div>
  );
}
