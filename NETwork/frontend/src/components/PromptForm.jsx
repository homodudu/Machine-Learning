/**
 * PromptForm component for NETwork chat application.
 * - Handles user input and message submission.
 * - Updates conversation state and triggers bot response.
 * - Displays a send button and manages loading state.
 * - Auto-grows textarea as user types more lines.
 */

import { ArrowUp } from "lucide-react";
import { useState, useRef, useEffect } from "react";

const PromptForm = ({
  conversations,
  setConversations,
  activeConversation,
  generateResponse,
  isLoading,
  setIsLoading,
}) => {
  const [promptText, setPromptText] = useState("");
  const textareaRef = useRef(null);

  // Auto-grow textarea height as user types more lines
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"; // Reset height
      textareaRef.current.style.height = textareaRef.current.scrollHeight + "px"; // Set to scrollHeight
    }
  }, [promptText]);

  // Ensure the user cannot submit empty message while response is still loading
  const handleSubmit = (e) => {
    e.preventDefault();
    if (isLoading || !promptText.trim()) return;

    setIsLoading(true);

    const currentConvo =
      conversations.find((convo) => convo.id === activeConversation) || conversations[0];

    // Set conversation title from first message if new chat (with "thinking" message)
    const newTitle =
      currentConvo.messages.length === 0
        ? promptText.length > 25
          ? promptText.substring(0, 25) + "..."
          : promptText
        : currentConvo.title;

    // Add user message
    const userMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: promptText,
    };

    // Prepare conversation for API (without "thinking" message)
    const apiConversation = {
      ...currentConvo,
      messages: [...currentConvo.messages, userMessage],
    };

    // Update UI with user message
    setConversations((prev) =>
      prev.map((conv) =>
        conv.id === activeConversation
          ? { ...conv, title: newTitle, messages: [...conv.messages, userMessage] }
          : conv
      )
    );

    setPromptText("");

    // Add bot "thinking" message after short delay
    setTimeout(() => {
      const botMessageId = `bot-${Date.now()}`;
      const botMessage = {
        id: botMessageId,
        role: "bot",
        content: "...",
        loading: true,
      };

       // Update UI with bot message
      setConversations((prev) =>
        prev.map((conv) =>
          conv.id === activeConversation
            ? { ...conv, title: newTitle, messages: [...conv.messages, botMessage] }
            : conv
        )
      );

      // Trigger backend API call to generate response for the user prompt
      generateResponse(apiConversation, botMessageId);
    }, 300);
  };

  return (
    //Render
    <form className="prompt-form" onSubmit={handleSubmit}>
      <textarea
        id="prompt-input"
        name="prompt"
        placeholder="Message NETwork..."
        autoComplete="off"
        className="prompt-input"
        value={promptText}
        onChange={(e) => setPromptText(e.target.value)}
        required
        rows={1}
        style={{ resize: "vertical" }}
        title="Enter a message. Press Shift + Enter to add a new line."
        ref={textareaRef}
        onKeyDown={e => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
          }
        }}
      />
      <button type="submit" className="send-prompt-btn">
        <ArrowUp size={20} />
      </button>
    </form>
  );
};

export default PromptForm;
