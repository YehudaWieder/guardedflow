// Minimal hand-drawn icons, not an icon library dependency — each node kind
// just needs one small, recognizable glyph.

export function AgentIcon() {
  return (
    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" aria-hidden="true">
      <path d="M12 3v3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <circle cx="12" cy="3" r="1.3" fill="currentColor" />
      <rect x="4" y="6.5" width="16" height="12.5" rx="3.5" stroke="currentColor" strokeWidth="1.8" />
      <circle cx="9" cy="12.5" r="1.4" fill="currentColor" />
      <circle cx="15" cy="12.5" r="1.4" fill="currentColor" />
      <path d="M9 16h6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

// Just a face — used inside the Agent node's round "head", which supplies
// the circle itself via CSS.
export function AgentFace() {
  return (
    <svg viewBox="0 0 24 24" width="13" height="13" fill="none" aria-hidden="true">
      <circle cx="8.5" cy="12" r="1.8" fill="currentColor" />
      <circle cx="15.5" cy="12" r="1.8" fill="currentColor" />
      <path d="M8.5 16.5h7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

export function ToolIcon() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" aria-hidden="true">
      <path
        d="M14.7 6.3a4 4 0 0 0-5.1 5.1L4 17l3 3 5.6-5.6a4 4 0 0 0 5.1-5.1l-2.3 2.3-2.6-.3-.3-2.6z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
