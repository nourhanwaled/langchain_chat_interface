"use client";

import React, { useState, useEffect, useRef } from "react";
import styles from "./Chat.module.css";

const API_URL = "http://localhost:8000";

interface Source {
  source: string;
  content: string;
}

interface Message {
  content: string;
  sources?: Source[];
}

const Chat: React.FC = () => {
  const [input, setInput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<
    Array<{
      role: "user" | "assistant";
      content: string;
      timestamp: string;
      sender?: string;
    }>
  >([]);

  const chatEndRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    setMessages([
      {
        role: "assistant",
        content: "مرحباً! كيف يمكنني مساعدتك اليوم؟",
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        }),
        sender: "AI",
      },
    ]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    setError(null);
    const userMessage = {
      role: "user" as const,
      content: input,
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
      }),
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    setInput("");

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: currentInput }),
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(errorData || response.statusText);
      }

      const data = await response.json();
      const assistantMessage = {
        role: "assistant" as const,
        content: data.answer,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        }),
        sender: "AI",
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error:", error);
      const errorMessage = {
        role: "assistant" as const,
        content:
          "عذراً، حدث خطأ في الاتصال. يرجى التأكد من تشغيل الخادم المحلي والمحاولة مرة أخرى.",
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        }),
        sender: "AI",
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  const MessageBubble = ({
    message,
    isUser,
  }: {
    message: Message;
    isUser: boolean;
  }) => {
    // Function to format the message content
    const formatContent = (content: string) => {
      // نفصل بناءً على النجمة
      return content
        .split("*")
        .map((segment) => segment.trim()) // إزالة المسافات الزائدة
        .filter((segment) => segment.length > 0) // تجاهل الفقرات الفارغة
        .map((segment, index) => (
          <div key={index} className="message-line">
            {segment}
          </div>
        ));
    };

    return (
      <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
        <div
          className={`max-w-[80%] rounded-lg p-4 ${
            isUser ? "bg-blue-500 text-white" : "bg-gray-100 text-gray-900"
          }`}
        >
          <div
            className={`text-right ${isUser ? "" : "arabic-text"}`}
            dir="rtl"
          >
            {formatContent(message.content)}
          </div>
          {!isUser && message.sources && message.sources.length > 0 && (
            <div className="source-section">
              <div className="source-title">المصادر:</div>
              {message.sources.map((source: Source, index: number) => (
                <div key={index} className="source-item">
                  <div className="source-path">{source.source}</div>
                  <div className="source-preview">{source.content}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className={styles.chatContainer}>
      {/* Header */}
      <div className={styles.header}>
        <h1 className={styles.title}>مساعد الذكاء الاصطناعي</h1>
        <div className={styles.status}>
          <div className={styles.onlineDot}></div>
          <span className={styles.statusText}>متصل</span>
        </div>
      </div>

      {/* Chat Messages */}
      <div className={styles.messageContainer}>
        {messages.map((message, index) => (
          <div
            key={`${message.timestamp}-${index}`}
            className={styles.messageWrapper}
          >
            {message.role === "assistant" && (
              <div className={styles.sender}>{message.sender}</div>
            )}
            <div
              className={`${styles.message} ${
                message.role === "user"
                  ? styles.userMessage
                  : styles.assistantMessage
              }`}
            >
              {message.content}
            </div>
            <div className={styles.timestamp}>{message.timestamp}</div>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      {/* Input Area */}
      <div className={styles.inputContainer}>
        <form onSubmit={handleSubmit} className={styles.inputWrapper}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="اكتب رسالتك هنا..."
            className={styles.input}
          />
          <button
            type="submit"
            className={styles.sendButton}
            disabled={!input.trim()}
          >
            إرسال
          </button>
        </form>
        {error && <div className={styles.errorMessage}>{error}</div>}
      </div>
    </div>
  );
};

export default Chat;
