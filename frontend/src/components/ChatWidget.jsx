import React, { useState, useEffect, useRef } from "react";
import { chatApi } from "../services/taskApi";

function formatMessageText(text) {
  if (!text) return null;

  // Split by line
  const lines = text.split("\n");
  return lines.map((line, idx) => {
    // Check if bullet point
    const isBullet = line.trim().startsWith("- ") || line.trim().startsWith("• ");
    const content = isBullet ? line.trim().replace(/^[-•]\s*/, "") : line;

    // Format bold and code within the line
    const parts = [];
    let remaining = content;

    // Match bold **text** or `code` or *italic*
    const regex = /(\*\*.*?\*\*|\*.*?\*|`.*?`)/g;
    let match;
    let lastIndex = 0;

    while ((match = regex.exec(content)) !== null) {
      if (match.index > lastIndex) {
        parts.push(content.substring(lastIndex, match.index));
      }
      const raw = match[0];
      if (raw.startsWith("**") && raw.endsWith("**")) {
        parts.push(<strong key={`${idx}-${match.index}`}>{raw.slice(2, -2)}</strong>);
      } else if (raw.startsWith("`") && raw.endsWith("`")) {
        parts.push(<code key={`${idx}-${match.index}`} className="chat-inline-code">{raw.slice(1, -1)}</code>);
      } else if (raw.startsWith("*") && raw.endsWith("*")) {
        parts.push(<em key={`${idx}-${match.index}`}>{raw.slice(1, -1)}</em>);
      }
      lastIndex = regex.lastIndex;
    }
    if (lastIndex < content.length) {
      parts.push(content.substring(lastIndex));
    }

    if (isBullet) {
      return (
        <li key={idx} className="chat-bullet-item">
          {parts}
        </li>
      );
    }

    if (!line.trim()) {
      return <div key={idx} className="chat-spacer" />;
    }

    return <p key={idx} className="chat-paragraph">{parts}</p>;
  });
}

export default function ChatWidget({ onTasksChanged }) {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [batchAdding, setBatchAdding] = useState(false);
  const [suggestions, setSuggestions] = useState([
    "📋 Danh sách task cần làm",
    "✨ Tạo task Kiểm thử API ngày mai ưu tiên cao",
    "📊 Tóm tắt tiến độ công việc",
    "💡 Gợi ý kế hoạch làm website bán hàng"
  ]);

  const [messages, setMessages] = useState([
    {
      id: "init",
      role: "assistant",
      content:
        "👋 Xin chào! Tôi là **Trợ lý AI TaskFlow**.\nTôi có thể hỗ trợ bạn tạo task, tra cứu công việc, đánh dấu hoàn thành hoặc tóm tắt tiến độ.\n\nHãy thử chọn gợi ý bên dưới hoặc gõ câu lệnh của bạn!",
      action: null,
      timestamp: new Date()
    }
  ]);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
      setTimeout(() => inputRef.current?.focus(), 200);
    }
  }, [isOpen, messages]);

  // Load suggestions from API on mount
  useEffect(() => {
    chatApi.getSuggestions()
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          setSuggestions(data);
        }
      })
      .catch(() => {});
  }, []);

  const handleSendMessage = async (textToSend) => {
    const text = (textToSend || input).trim();
    if (!text || loading) return;

    const userMsg = {
      id: `user-${Date.now()}`,
      role: "user",
      content: text,
      timestamp: new Date()
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      // Build lightweight conversation history
      const history = messages
        .filter((m) => m.role === "user" || m.role === "assistant")
        .slice(-6)
        .map((m) => ({ role: m.role, content: m.content }));

      const res = await chatApi.sendMessage(text, history);

      const botMsg = {
        id: `bot-${Date.now()}`,
        role: "assistant",
        content: res.reply,
        action: res.action,
        llmUsed: res.llm_used,
        provider: res.provider,
        timestamp: new Date()
      };

      setMessages((prev) => [...prev, botMsg]);

      // If the action modified the DB (create, complete, delete), notify parent
      if (
        res.action &&
        ["create_task", "complete_task", "delete_task", "update_task"].includes(res.action.type)
      ) {
        if (onTasksChanged) onTasksChanged();
      }
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          id: `bot-err-${Date.now()}`,
          role: "assistant",
          content: `⚠️ Rất tiếc, đã xảy ra lỗi: ${err.message || "Không thể xử lý yêu cầu"}. Vui lòng thử lại.`,
          action: null,
          timestamp: new Date()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleBatchAddTasks = async (suggestedTasks) => {
    if (!suggestedTasks || suggestedTasks.length === 0 || batchAdding) return;
    setBatchAdding(true);
    try {
      await chatApi.batchCreateTasks(suggestedTasks);
      setMessages((prev) => [
        ...prev,
        {
          id: `bot-batch-${Date.now()}`,
          role: "assistant",
          content: `🎉 **Tuyệt vời!** Đã thêm thành công **${suggestedTasks.length} công việc** vào danh sách TaskFlow của bạn!`,
          action: null,
          timestamp: new Date()
        }
      ]);
      if (onTasksChanged) onTasksChanged();
    } catch (err) {
      alert("Lỗi khi thêm danh sách task: " + err.message);
    } finally {
      setBatchAdding(false);
    }
  };

  const handleAddSingleSuggestedTask = async (task) => {
    try {
      await chatApi.batchCreateTasks([task]);
      setMessages((prev) => [
        ...prev,
        {
          id: `bot-single-${Date.now()}`,
          role: "assistant",
          content: `✅ Đã thêm công việc: **"${task.title}"** vào TaskFlow!`,
          action: null,
          timestamp: new Date()
        }
      ]);
      if (onTasksChanged) onTasksChanged();
    } catch (err) {
      alert("Lỗi khi thêm task: " + err.message);
    }
  };

  const handleClearHistory = () => {
    setMessages([
      {
        id: `init-${Date.now()}`,
        role: "assistant",
        content: "👋 Lịch sử trò chuyện đã được làm mới. Tôi có thể hỗ trợ gì cho bạn?",
        action: null,
        timestamp: new Date()
      }
    ]);
  };

  return (
    <aside className="chat-widget-container" aria-label="Khung trò chuyện Trợ lý AI TaskFlow">
      {/* Floating Toggle Button */}
      {!isOpen && (
        <button
          className="chat-toggle-btn"
          onClick={() => setIsOpen(true)}
          title="Mở Trợ lý AI TaskFlow"
          aria-expanded="false"
        >
          <div className="chat-toggle-icon-wrap">
            <span className="chat-sparkle-icon">✨</span>
            <span className="chat-bot-icon">💬</span>
          </div>
          <span className="chat-toggle-label">Hỏi Trợ lý AI</span>
          <span className="chat-online-dot"></span>
        </button>
      )}

      {/* Chat Window Panel */}
      {isOpen && (
        <div className="chat-window">
          {/* Header */}
          <div className="chat-header">
            <div className="chat-header-info">
              <div className="chat-avatar">
                <span>🤖</span>
                <span className="avatar-status-badge"></span>
              </div>
              <div>
                <h3 className="chat-title">
                  TaskFlow AI Assistant
                  <span className="chat-badge-ai">AI Pro</span>
                </h3>
                <span className="chat-subtitle">Hỗ trợ quản lý & tự động hóa task</span>
              </div>
            </div>
            <div className="chat-header-actions">
              <button
                className="chat-btn-icon"
                onClick={handleClearHistory}
                title="Làm mới cuộc trò chuyện"
              >
                🔄
              </button>
              <button
                className="chat-btn-icon"
                onClick={() => setIsOpen(false)}
                title="Thu nhỏ"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Quick Suggestion Chips */}
          <div className="chat-chips-container">
            {suggestions.slice(0, 4).map((sugg, i) => (
              <button
                key={i}
                className="chat-chip-btn"
                onClick={() => handleSendMessage(sugg)}
                disabled={loading}
              >
                {sugg}
              </button>
            ))}
          </div>

          {/* Messages Body */}
          <div className="chat-messages-body">
            {messages.map((m) => {
              const isUser = m.role === "user";
              return (
                <div
                  key={m.id}
                  className={`chat-message-row ${isUser ? "user-row" : "bot-row"}`}
                >
                  {!isUser && (
                    <div className="chat-bubble-avatar">
                      <span>🤖</span>
                    </div>
                  )}

                  <div className={`chat-bubble ${isUser ? "user-bubble" : "bot-bubble"}`}>
                    <div className="chat-bubble-content">
                      {formatMessageText(m.content)}
                    </div>

                    {/* Interactive Action: Create Task Card */}
                    {m.action && m.action.type === "create_task" && m.action.task && (
                      <div className="chat-action-card task-created-card">
                        <div className="action-card-header">
                          <span className="action-badge-created">ĐÃ TẠO MỚI</span>
                          <span className="action-task-id">#{m.action.task.id}</span>
                        </div>
                        <h4 className="action-task-title">{m.action.task.title}</h4>
                        <div className="action-task-meta">
                          <span className={`priority-badge priority-${m.action.task.priority}`}>
                            {m.action.task.priority.toUpperCase()}
                          </span>
                          {m.action.task.due_date && (
                            <span className="action-due-date">
                              📅 {m.action.task.due_date}
                            </span>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Interactive Action: Suggested Tasks Project Breakdown */}
                    {m.action && m.action.type === "suggest_tasks" && m.action.suggested_tasks && (
                      <div className="chat-action-card task-suggest-card">
                        <div className="action-card-header">
                          <span className="action-badge-suggest">GỢI Ý KẾ HOẠCH</span>
                          <span className="suggest-count">
                            {m.action.suggested_tasks.length} nhiệm vụ
                          </span>
                        </div>
                        <div className="suggested-task-list">
                          {m.action.suggested_tasks.map((task, idx) => (
                            <div key={idx} className="suggested-task-item">
                              <div className="suggested-task-info">
                                <strong>{idx + 1}. {task.title}</strong>
                                {task.description && <p>{task.description}</p>}
                              </div>
                              <button
                                className="btn-add-single"
                                title="Thêm công việc này"
                                onClick={() => handleAddSingleSuggestedTask(task)}
                              >
                                ＋
                              </button>
                            </div>
                          ))}
                        </div>
                        <button
                          className="btn-add-all-suggested"
                          disabled={batchAdding}
                          onClick={() => handleBatchAddTasks(m.action.suggested_tasks)}
                        >
                          {batchAdding ? "Đang thêm..." : "✨ Thêm tất cả vào TaskFlow"}
                        </button>
                      </div>
                    )}

                    {/* Interactive Action: Progress Summary Card */}
                    {m.action && m.action.type === "summary" && m.action.summary_data && (
                      <div className="chat-action-card task-summary-card">
                        <div className="summary-progress-bar-wrap">
                          <div className="summary-progress-label">
                            <span>Tỷ lệ hoàn thành</span>
                            <strong>{m.action.summary_data.completion_rate}%</strong>
                          </div>
                          <div className="summary-progress-track">
                            <div
                              className="summary-progress-fill"
                              style={{ width: `${m.action.summary_data.completion_rate}%` }}
                            />
                          </div>
                        </div>
                        <div className="summary-stats-grid">
                          <div className="summary-stat-box">
                            <span className="stat-num">{m.action.summary_data.total}</span>
                            <span className="stat-lbl">Tổng task</span>
                          </div>
                          <div className="summary-stat-box stat-completed">
                            <span className="stat-num">{m.action.summary_data.completed}</span>
                            <span className="stat-lbl">Đã xong</span>
                          </div>
                          <div className="summary-stat-box stat-pending">
                            <span className="stat-num">{m.action.summary_data.pending}</span>
                            <span className="stat-lbl">Đang chờ</span>
                          </div>
                          <div className="summary-stat-box stat-urgent">
                            <span className="stat-num">{m.action.summary_data.high_priority_pending}</span>
                            <span className="stat-lbl">Ưu tiên cao</span>
                          </div>
                        </div>
                      </div>
                    )}

                    <div className="chat-bubble-footer">
                      {m.provider && <span className="provider-tag">{m.provider}</span>}
                      <span className="bubble-time">
                        {new Date(m.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}

            {loading && (
              <div className="chat-message-row bot-row">
                <div className="chat-bubble-avatar">
                  <span>🤖</span>
                </div>
                <div className="chat-bubble bot-bubble typing-bubble">
                  <div className="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <span className="typing-text">AI đang phân tích và xử lý...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Footer */}
          <div className="chat-input-bar">
            <textarea
              ref={inputRef}
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Nhập yêu cầu: tạo task, tóm tắt, tìm kiếm..."
              className="chat-textarea"
              disabled={loading}
            />
            <button
              onClick={() => handleSendMessage()}
              disabled={!input.trim() || loading}
              className="chat-send-btn"
              title="Gửi tin nhắn"
            >
              {loading ? (
                <span className="chat-spinner"></span>
              ) : (
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
              )}
            </button>
          </div>
        </div>
      )}
    </aside>
  );
}
