"use client";

import React, { useState, useEffect } from "react";
import styles from "./Chat.module.css";

const Chat: React.FC = () => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<
    Array<{
      role: "user" | "assistant";
      content: string;
      timestamp: string;
      sender?: string;
    }>
  >([]);

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

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
    setInput("");

    try {
      const response = await fetch(
        "https://a71e-35-243-157-175.ngrok-free.app/ask",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ question: input }),
        }
      );

      if (!response.ok) throw new Error("Failed to fetch response");

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
    }
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
      </div>
    </div>
  );
};

export default Chat;
