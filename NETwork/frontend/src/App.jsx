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

// Define the default conversation object
const DEFAULT_CONVERSATION = { id: "default", title: "New Chat", messages: [] };

// Define the backend API endpoint for generating a response.
const REACT_APP_GENERATE_RESPONSE_ENDPOINT =
  process.env.NODE_ENV === "production"
    ? "https://network-api-d8dxcph2d8b9csfj.westeurope-01.azurewebsites.net/api/generate_response"
    : process.env.REACT_APP_GENERATE_RESPONSE_ENDPOINT_DEV;

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

  // Load stored conversations on first load
  const [conversations, setConversations] = useState(() => {
    try {
      // Only load saved conversations if they exist, otherwise use default conversation
      const saved = localStorage.getItem("conversations");
      return saved ? JSON.parse(saved) : [DEFAULT_CONVERSATION];
    } catch {
      return [DEFAULT_CONVERSATION];
    }
  });

  // Set saved active conversation if it exists, set default active conversation
  const [activeConversation, setActiveConversation] = useState(() =>
    localStorage.getItem("activeConversation") || "default"
  );

  // Refs
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

  const displayBotMessage = (text, messageId) => {
    setConversations((prev) =>
      prev.map((conv) =>
        conv.id === activeConversation
          ? {
              ...conv,
              messages: conv.messages.map((msg) =>
                msg.id === messageId ? { ...msg, content: text, loading: false } : msg
              ),
            }
          : conv
      )
    );
    scrollToBottom();
    setIsLoading(false);
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
  // Format messages for the API request
  const formattedMessages = conversation.messages?.map((msg) => ({
    role: msg.role === "bot" ? "assistant" : msg.role,
    content: msg.content,
  }));
  try {
    // Make a POST request to the API backend endpoint
    const res = await fetch(REACT_APP_GENERATE_RESPONSE_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contents: formattedMessages, thread_id: conversation.thread_id || null }),
    });
    // Parse the JSON response
    const data = await res.json();
    const threadId = data.thread_id; // Extract thread ID from response
    console.log("Agent API response:", data);

    // Update the conversation state with new thread ID
    setConversations((prev) =>
      prev.map((conv) =>
        conv.id === conversation.id
        ? { ...conv, thread_id: threadId }
        : conv
      )
    );

    // Check for errors in the response
    if (!res.ok) throw new Error(data.error?.message || "API error");

    // Handle the response text
    const responseText = typeof data.response === "string" ? data.response.trim(): "No response from agent.";
    displayBotMessage(responseText, botMessageId); // Display the response
  } catch (error) {
    setIsLoading(false); // Stop loading state
    updateBotMessage(botMessageId, error.message, true); // Update the bot message with the error
  }
};

  // Render
  return (
    <div className={`app-container ${theme === "light" ? "light-theme" : "dark-theme"}`}>
      {/* Main div container that wraps application */}
      <div
        //Overlay div container that appears when the sidebar is open and unlocked
        className={`overlay ${isSidebarOpen & !sidebarLocked ? "show" : "hide"}`}
        onClick={() => {
          setIsSidebarOpen(false);
          setSidebarLocked(false);
        }}
      >
      </div>
        {/* Main container that contains header, messages, prompt and footer elements */}
      <main className="main-container">
        <header className="main-header">
          {/* A header with a menu button to toggle the sidebar. */}
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
          {/* A messages container that displays either a welcome message or a list of messages */}
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
          {currentConversation.messages.map((message) => (
            <Message key={message.id} message={message} theme={theme} />
          ))}
        </div>
        <div className="prompt-container">
          {/* A prompt container for user input. */}
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
          {/* A footer with a disclaimer about the AI-generated responses. */}
          An AI-powered multi-agent chat application delivering tennis instruction, forecasts, betting insights, and strategic recommendations.
          <br />
          Responses are generated by AI for informational purposes only and should not be considered professional advice. Always verify important information independently.
        </p>
      </main>
      <Sidebar
        // A Sidebar component that manages conversations and theme settings.
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
}

export default App;
