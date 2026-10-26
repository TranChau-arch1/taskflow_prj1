const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  try {
    const res = await fetch(url, { ...options, headers });
    if (!res.ok) {
      let errorDetail = `Lỗi ${res.status}: ${res.statusText}`;
      try {
        const errorJson = await res.json();
        if (errorJson.detail) {
          if (Array.isArray(errorJson.detail)) {
            errorDetail = errorJson.detail.map((e) => `${e.loc?.join(".") || ""}: ${e.msg}`).join(", ");
          } else {
            errorDetail = errorJson.detail;
          }
        }
      } catch {
        // fallback to text error
      }
      throw new Error(errorDetail);
    }

    if (res.status === 204) return null;
    return await res.json();
  } catch (error) {
    if (error.name === "TypeError" && error.message.includes("Failed to fetch")) {
      throw new Error(`Không thể kết nối tới server API (${API_BASE_URL}). Vui lòng kiểm tra backend hoặc CORS.`);
    }
    throw error;
  }
}

export const taskApi = {
  async getTasks({ status, priority, search } = {}) {
    const params = new URLSearchParams();
    if (status && status !== "all") params.append("status", status);
    if (priority && priority !== "all") params.append("priority", priority);
    if (search && search.trim()) params.append("search", search.trim());

    const queryString = params.toString() ? `?${params.toString()}` : "";
    return await request(`/api/tasks${queryString}`);
  },

  async getTask(id) {
    return await request(`/api/tasks/${id}`);
  },

  async createTask(data) {
    return await request("/api/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async updateTask(id, data) {
    return await request(`/api/tasks/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  async toggleComplete(id) {
    return await request(`/api/tasks/${id}/complete`, {
      method: "PATCH",
    });
  },

  async deleteTask(id) {
    return await request(`/api/tasks/${id}`, {
      method: "DELETE",
    });
  },

  async checkHealth() {
    return await request("/health");
  },

  getBaseUrl() {
    return API_BASE_URL;
  }
};

export const chatApi = {
  async sendMessage(message, history = []) {
    return await request("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message, history }),
    });
  },

  async getSuggestions() {
    return await request("/api/chat/suggestions");
  },

  async batchCreateTasks(tasks) {
    return await request("/api/chat/batch-create", {
      method: "POST",
      body: JSON.stringify(tasks),
    });
  }
};
