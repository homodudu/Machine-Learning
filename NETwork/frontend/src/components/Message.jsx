/**
 * Message component for NETwork chat application.
 * - Renders a chat message with avatar for bot/user.
 * - Applies loading and error styles.
 * - Dynamically selects avatar based on theme.
 */

const Message = ({ message, theme }) => {
  const isBot = message.role === "bot";
  const avatarSrc = theme === "light" ? "NETwork Black.svg" : "NETwork White.svg";

  return (
    <div
      id={message.id}
      className={[
        "message",
        `${message.role}-message`,
        message.loading && "loading",
        message.error && "error"
      ].filter(Boolean).join(" ")}
    >
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
