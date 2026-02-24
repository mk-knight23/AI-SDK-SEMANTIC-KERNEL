import { useState, useEffect } from "react";
import "./MemoryComponent.css";

interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

interface SemanticMemoryItem {
  key: string;
  value: string;
}

export default function MemoryComponent() {
  const [activeTab, setActiveTab] = useState<"conversations" | "semantic">(
    "conversations",
  );
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [semanticMemory, setSemanticMemory] = useState<SemanticMemoryItem[]>(
    [],
  );
  const [newMemoryKey, setNewMemoryKey] = useState("");
  const [newMemoryValue, setNewMemoryValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (activeTab === "conversations") {
      loadConversations();
    } else {
      loadSemanticMemory();
    }
  }, [activeTab]);

  const loadConversations = async () => {
    try {
      const response = await fetch("/api/conversations");
      if (!response.ok) throw new Error("Failed to load conversations");
      const data = await response.json();
      setConversations(data.conversations);
    } catch (error) {
      console.error("Failed to load conversations:", error);
    }
  };

  const loadSemanticMemory = async () => {
    try {
      const response = await fetch("/api/memory/semantic/keys");
      if (!response.ok) throw new Error("Failed to load memory keys");
      const data = await response.json();

      const items = await Promise.all(
        data.keys.map(async (key: string) => {
          const res = await fetch(
            `/api/memory/semantic?key=${encodeURIComponent(key)}`,
          );
          const val = await res.json();
          return { key, value: JSON.stringify(val.value, null, 2) };
        }),
      );

      setSemanticMemory(items);
    } catch (error) {
      console.error("Failed to load semantic memory:", error);
    }
  };

  const handleSaveMemory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMemoryKey.trim() || !newMemoryValue.trim()) return;

    setIsLoading(true);
    try {
      const response = await fetch("/api/memory/semantic", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          key: newMemoryKey,
          value: newMemoryValue,
        }),
      });

      if (!response.ok) throw new Error("Failed to save memory");

      setNewMemoryKey("");
      setNewMemoryValue("");
      loadSemanticMemory();
    } catch (error) {
      console.error("Failed to save memory:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteMemory = async (key: string) => {
    try {
      await fetch(`/api/memory/semantic?key=${encodeURIComponent(key)}`, {
        method: "DELETE",
      });
      loadSemanticMemory();
    } catch (error) {
      console.error("Failed to delete memory:", error);
    }
  };

  const handleDeleteConversation = async (id: string) => {
    try {
      await fetch(`/api/conversations/${id}`, {
        method: "DELETE",
      });
      loadConversations();
    } catch (error) {
      console.error("Failed to delete conversation:", error);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="memory-container">
      <div className="tabs">
        <button
          className={`tab ${activeTab === "conversations" ? "active" : ""}`}
          onClick={() => setActiveTab("conversations")}
        >
          Conversations
        </button>
        <button
          className={`tab ${activeTab === "semantic" ? "active" : ""}`}
          onClick={() => setActiveTab("semantic")}
        >
          Semantic Memory
        </button>
      </div>

      {activeTab === "conversations" && (
        <div className="tab-content">
          {conversations.length === 0 ? (
            <div className="empty-state">No conversations yet</div>
          ) : (
            <div className="conversations-list">
              {conversations.map((conv) => (
                <div key={conv.id} className="conversation-card">
                  <div className="conversation-header">
                    <h3>{conv.title}</h3>
                    <button
                      onClick={() => handleDeleteConversation(conv.id)}
                      className="btn-icon"
                      title="Delete conversation"
                    >
                      ×
                    </button>
                  </div>
                  <div className="conversation-meta">
                    <span>{conv.message_count} messages</span>
                    <span>Created: {formatDate(conv.created_at)}</span>
                  </div>
                  <div className="conversation-footer">
                    <span>Updated: {formatDate(conv.updated_at)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === "semantic" && (
        <div className="tab-content">
          <form onSubmit={handleSaveMemory} className="memory-form">
            <div className="form-row">
              <input
                type="text"
                placeholder="Key"
                value={newMemoryKey}
                onChange={(e) => setNewMemoryKey(e.target.value)}
                className="input-text"
              />
              <textarea
                placeholder="Value (JSON)"
                value={newMemoryValue}
                onChange={(e) => setNewMemoryValue(e.target.value)}
                rows={3}
                className="input-textarea"
              />
            </div>
            <button
              type="submit"
              disabled={
                isLoading || !newMemoryKey.trim() || !newMemoryValue.trim()
              }
              className="btn btn-primary"
            >
              {isLoading ? "Saving..." : "Save Memory"}
            </button>
          </form>

          {semanticMemory.length === 0 ? (
            <div className="empty-state">No semantic memory stored</div>
          ) : (
            <div className="memory-list">
              {semanticMemory.map((item) => (
                <div key={item.key} className="memory-card">
                  <div className="memory-header">
                    <code>{item.key}</code>
                    <button
                      onClick={() => handleDeleteMemory(item.key)}
                      className="btn-icon"
                      title="Delete memory"
                    >
                      ×
                    </button>
                  </div>
                  <pre className="memory-value">{item.value}</pre>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
