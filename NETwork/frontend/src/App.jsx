/**
 * Main App component for NETwork.
 * - Manages theme, sidebar state, conversations, and active chat.
 * - Handles message typing effect, API calls, and localStorage persistence.
 * - Renders sidebar, chat messages, prompt input, and welcome screen.
 */

import { useEffect, useRef, useState } from "react";
import Message from "./components/Message";
import PromptForm from "./components/PromptForm";
import Sidebar from "./components/Sidebar";
import { Menu } from "lucide-react";

const DEFAULT_CONVERSATION = { id: "default", title: "New Chat", messages: [] };

const App = () => {
  // State
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [sidebarLocked, setSidebarLocked] = useState(false);
  // Use system theme preference on first load
  const [theme, setTheme] = useState(() => {
    // Only use saved theme if it exists, otherwise use system preference
    const saved = localStorage.getItem("theme");
    if (saved) return saved;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  });
  const [conversations, setConversations] = useState(() => {
    try {
      const saved = localStorage.getItem("conversations");
      return saved ? JSON.parse(saved) : [DEFAULT_CONVERSATION];
    } catch {
      return [DEFAULT_CONVERSATION];
    }
  });
  const [activeConversation, setActiveConversation] = useState(() =>
    localStorage.getItem("activeConversation") || "default"
  );

  // Refs
  const typingInterval = useRef(null);
  const messagesContainerRef = useRef(null);

  // Effects
  useEffect(() => {
    localStorage.setItem("activeConversation", activeConversation);
  }, [activeConversation]);

  useEffect(() => {
    localStorage.setItem("conversations", JSON.stringify(conversations));
  }, [conversations]);

  useEffect(() => {
    localStorage.setItem("theme", theme);
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);

  useEffect(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTo({
        top: messagesContainerRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [conversations, activeConversation]);

  // Helpers
  const currentConversation =
    conversations.find((c) => c.id === activeConversation) || conversations[0];

  const scrollToBottom = () => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTo({
        top: messagesContainerRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  };

  const typingEffect = (text, messageId) => {
    let textElement = document.querySelector(`#${messageId} .text`);
    if (!textElement) return;
    setConversations((prev) =>
      prev.map((conv) =>
        conv.id === activeConversation
          ? {
              ...conv,
              messages: conv.messages.map((msg) =>
                msg.id === messageId ? { ...msg, content: "", loading: true } : msg
              ),
            }
          : conv
      )
    );
    textElement.textContent = "";
    const words = text.split(" ");
    let wordIndex = 0;
    let currentText = "";
    clearInterval(typingInterval.current);
    typingInterval.current = setInterval(() => {
      if (wordIndex < words.length) {
        currentText += (wordIndex === 0 ? "" : " ") + words[wordIndex++];
        textElement.textContent = currentText;
        setConversations((prev) =>
          prev.map((conv) =>
            conv.id === activeConversation
              ? {
                  ...conv,
                  messages: conv.messages.map((msg) =>
                    msg.id === messageId ? { ...msg, content: currentText, loading: true } : msg
                  ),
                }
              : conv
          )
        );
        scrollToBottom();
      } else {
        clearInterval(typingInterval.current);
        setConversations((prev) =>
          prev.map((conv) =>
            conv.id === activeConversation
              ? {
                  ...conv,
                  messages: conv.messages.map((msg) =>
                    msg.id === messageId ? { ...msg, content: currentText, loading: false } : msg
                  ),
                }
              : conv
          )
        );
        setIsLoading(false);
      }
    }, 40);
  };

  const updateBotMessage = (botId, content, isError = false) => {
    setConversations((prev) =>
      prev.map((conv) =>
        conv.id === activeConversation
          ? {
              ...conv,
              messages: conv.messages.map((msg) =>
                msg.id === botId ? { ...msg, content, loading: false, error: isError } : msg
              ),
            }
          : conv
      )
    );
  };

const generateResponse = async (conversation, botMessageId) => {
  const formattedMessages = conversation.messages?.map((msg) => ({
    role: msg.role === "bot" ? "assistant" : msg.role,
    content: msg.content,
  }));
  try {
    const res = await fetch(process.env.REACT_APP_GENERATE_RESPONSE_ENDPOINT_DEV, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contents: formattedMessages, thread_id: conversation.thread_id || null }),
    });
    const data = await res.json();
    const threadId = data.thread_id;
    console.log("Agent API response:", data);

    // Store threadId in the current conversation
    setConversations((prev) =>
      prev.map((conv) =>
        conv.id === conversation.id
        ? { ...conv, thread_id: threadId }
        : conv
      )
    );

    if (!res.ok) throw new Error(data.error?.message || "API error");
    const responseText = typeof data.response === "string" ? data.response.trim(): "No response from agent.";
    typingEffect(responseText, botMessageId);
  } catch (error) {
    setIsLoading(false);
    updateBotMessage(botMessageId, error.message, true);
  }
};

  // Render
  return (
    <div className={`app-container ${theme === "light" ? "light-theme" : "dark-theme"}`}>
      <div
        className={`overlay ${isSidebarOpen & !sidebarLocked ? "show" : "hide"}`}
        onClick={() => {
          setIsSidebarOpen(false);
          setSidebarLocked(false);
        }}
      ></div>
      <main className="main-container">
        <header className="main-header">
          <button
            onClick={() => {
              setIsSidebarOpen(true);
              setSidebarLocked((prev) => !prev);
            }}
            className="sidebar-pin"
          >
            <Menu size={18} />
          </button>
        </header>
        <div className="messages-container" ref={messagesContainerRef}>
          {/* Show welcome screen only when there are no messages */}
          {currentConversation.messages.length === 0 && (
            <div className="welcome-logo-wrapper">
              <img
                className="welcome-logo"
                src={theme === "light" ? "NETwork Black.svg" : "NETwork White.svg"}
                alt="NETwork Logo"
              />
              <h1 className="welcome-heading">NETwork</h1>
            </div>
          )}
          {/* Always render the messages list */}
          {currentConversation.messages.map((message) => (
            <Message key={message.id} message={message} theme={theme} />
          ))}
        </div>
        <div className="prompt-container">
          <div className="prompt-wrapper">
            <PromptForm
              conversations={conversations}
              setConversations={setConversations}
              activeConversation={activeConversation}
              generateResponse={generateResponse}
              isLoading={isLoading}
              setIsLoading={setIsLoading}
            />
          </div>
        </div>
        <p className="welcome-text">
          An AI-powered multi-agent chat application delivering tennis instruction, forecasts, betting insights, and strategic recommendations.<br />
          Responses are generated by AI for informational purposes only and should not be considered professional advice. Always verify important information independently.
        </p>
      </main>
      <Sidebar
        isSidebarOpen={isSidebarOpen}
        setIsSidebarOpen={setIsSidebarOpen}
        sidebarLocked={sidebarLocked}
        setSidebarLocked={setSidebarLocked}
        conversations={conversations}
        setConversations={setConversations}
        activeConversation={activeConversation}
        setActiveConversation={setActiveConversation}
        theme={theme}
        setTheme={setTheme}
        onMouseEnter={() => { if (!sidebarLocked) setIsSidebarOpen(true); }}
        onMouseLeave={() => { if (!sidebarLocked) setIsSidebarOpen(false); }}
      />
    </div>
  );
};

export default App;
