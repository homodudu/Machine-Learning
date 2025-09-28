/**
 * Message component for NETwork chat application.
 * - Renders user and bot chat messages.
 * - Applies loading and error styles.
 * - Applies avatar is the message is from a bot.
 * - Dynamically selects avatar colour based on theme.
 */

const Message = ({ message, theme }) => {
  // Determine if the message is from a bot
  const isBot = message.role === "bot";

  // Select the appropriate avatar based on the theme
  const avatarSrc = theme === "light" ? "NETwork Black.svg" : "NETwork White.svg";

  return (
    //Render
    <div
      id={message.id}
      className={[
        "message",
        `${message.role}-message`,
        message.loading && "loading",
        message.error && "error"
      ].filter(Boolean).join(" ")}
    >
      {/* Only render avatar if the message is from a bot */}
      {isBot && (
        <img
          className="avatar"
          src={avatarSrc}
          alt="NETwork Avatar"
        />
      )}
      <p className="text">{message.content}</p>
    </div>
  );
};

export default Message;
