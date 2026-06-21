interface ConnectionBadgeProps {
  connected: boolean;
}

export function ConnectionBadge({ connected }: ConnectionBadgeProps) {
  return (
    <span
      aria-live="polite"
      className={`connection-badge connection-badge--${
        connected ? "online" : "offline"
      }`}
      title={
        connected
          ? "Live updates connected"
          : "Reconnecting to local runtime…"
      }
    >
      <span aria-hidden="true" className="connection-dot" />
      {connected ? "Live" : "Reconnecting"}
    </span>
  );
}
