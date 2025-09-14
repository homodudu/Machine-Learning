/**
 * Sidebar component for NETwork chat application.
 * - Displays chat history, new chat button, theme toggle, and sidebar pin.
 * - Handles sidebar open/close, locking, and conversation management.
 * - Responsive to theme and sidebar state.
 */

import { Pin, Moon, Plus, History, Sun, Trash2 } from "lucide-react";

const Sidebar = ({
  isSidebarOpen,
  setIsSidebarOpen,
  sidebarLocked,
  setSidebarLocked,
  conversations,
  setConversations,
  activeConversation,
  setActiveConversation,
  theme,
  setTheme,
  onMouseEnter = () => {},
  onMouseLeave = () => {},
}) => {
  // Create new conversation or activate empty one
  const createNewConversation = () => {
    const emptyConv = conversations.find((conv) => conv.messages.length === 0);
    if (emptyConv) {
      setActiveConversation(emptyConv.id);
      return;
    }
    const newId = `conv-${Date.now()}`;
    setConversations([{ id: newId, title: "New Chat", messages: [] }, ...conversations]);
    setActiveConversation(newId);
  };

  // Delete conversation
  const deleteConversation = (id) => {
    if (conversations.length === 1) {
      const newConv = { id: "default", title: "New Chat", messages: [] };
      setConversations([newConv]);
      setActiveConversation("default");
    } else {
      const updatedConvs = conversations.filter((conv) => conv.id !== id);
      setConversations(updatedConvs);
      if (activeConversation === id) {
        setActiveConversation(updatedConvs[0].id);
      }
    }
  };

  return (
    <aside
      className={`sidebar ${isSidebarOpen ? "open" : "closed"}${sidebarLocked ? " sidebar-locked" : ""}`}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      {/* Sidebar Header */}
      <div className="sidebar-header">
        <button
          className="sidebar-pin"
          title="Toggle the sidebar pin."
          onClick={() => {
            setIsSidebarOpen(true);
            setSidebarLocked((prev) => !prev);
          }}
        >
          <Pin size={22} />
        </button>
          <button
            className="new-chat-btn"
            title="Start a new chat."
            onClick={createNewConversation}
          >
          <Plus size={20} />
          <span>New chat</span>
        </button>
      </div>
      {/* Conversation List */}
      <div className="sidebar-content">
        <h2 className="sidebar-title">Chat history</h2>
        <ul className="conversation-list">
          {conversations.map((conv) => (
            <li
              key={conv.id}
              className={`conversation-item${activeConversation === conv.id ? " active" : ""}`}
              onClick={() => setActiveConversation(conv.id)}
            >
              <div className="conversation-icon-title">
                <div className="conversation-icon">
                  <History size={14} />
                </div>
                <span className="conversation-title">{conv.title}</span>
              </div>
              <button
                className={`delete-btn${conversations.length > 1 || conv.title !== "New Chat" ? "" : " hide"}`}
                onClick={(e) => deleteConversation(conv.id, conv.thread_Id, e)}
              >
                <Trash2 size={16} />
              </button>
            </li>
          ))}
        </ul>
      </div>
      {/* Theme Toggle */}
      <div className="sidebar-footer">
        <button className="theme-toggle"
          onClick={() => setTheme(theme === "light" ? "dark" : "light")}
          title="Toggle the chat theme."
        >
          {theme === "light" ? (
            <>
              <Moon size={20} />
              <span>Dark</span>
            </>
          ) : (
            <>
              <Sun size={20} />
              <span>Light</span>
            </>
          )}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
