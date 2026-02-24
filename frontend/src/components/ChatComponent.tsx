import { useState, useRef, useEffect } from "react";
import "./ChatComponent.css";

interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp?: string;
}

interface ChatResponse {
  conversation_id: string;
  message_id: string;
  content: string;
  function_calls?: any[];
}

export default function ChatComponent() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [status, setStatus] = useState<{
    configured: boolean;
    model?: string;
  } | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Check kernel status
    fetch("/api/status")
      .then((res) => res.json())
      .then((data) => {
        setStatus({
          configured: data.configured,
          model: data.model,
        });
      })
      .catch(() => {
        setStatus({ configured: false });
      });
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMessage.content,
          conversation_id: conversationId,
          use_plugins: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data: ChatResponse = await response.json();

      setConversationId(data.conversation_id);

      const assistantMessage: Message = {
        id: data.message_id,
        role: "assistant",
        content: data.content,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: "system",
        content: `Error: ${error instanceof Error ? error.message : "Failed to send message"}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const startNewChat = () => {
    setMessages([]);
    setConversationId(null);
  };

  if (status && !status.configured) {
    return (
      <div className="chat-container">
        <div className="error-banner">
          <h2>Kernel Not Configured</h2>
          <p>
            Please set the AI_API_KEY environment variable to use this
            application.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="chat-header-content">
          <h1>Semantic Kernel Chat</h1>
          {status?.model && <span className="model-badge">{status.model}</span>}
        </div>
        <button onClick={startNewChat} className="btn btn-outline btn-sm">
          New Chat
        </button>
      </div>

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">💬</div>
            <h2>Start a conversation</h2>
            <p>
              Ask me anything! I have access to plugins for time, weather,
              calculations, and more.
            </p>
            <div className="suggestions">
              <button
                onClick={() => setInput("What time is it?")}
                className="suggestion-chip"
              >
                🕐 What time is it?
              </button>
              <button
                onClick={() => setInput("What's the weather in Tokyo?")}
                className="suggestion-chip"
              >
                🌤️ Weather in Tokyo?
              </button>
              <button
                onClick={() => setInput("Calculate 25 * 47")}
                className="suggestion-chip"
              >
                🔢 25 * 47?
              </button>
              <button
                onClick={() => setInput("Count the words in this sentence")}
                className="suggestion-chip"
              >
                📝 Count words
              </button>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`message-bubble message-${message.role}`}
              >
                {message.content}
              </div>
            ))}
            {isLoading && (
              <div className="message-bubble message-assistant">
                <div className="spinner" />
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={isLoading}
          className="message-input"
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="send-button"
        >
          {isLoading ? "..." : "Send"}
        </button>
      </form>
    </div>
  );
}
