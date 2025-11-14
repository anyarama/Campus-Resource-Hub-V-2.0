import React from "react";

interface AuthToggleProps {
  active: "login" | "signup";
  onSelectLogin?: () => void;
  onSelectSignup?: () => void;
  width?: number;
}

export function AuthToggle({ active, onSelectLogin, onSelectSignup, width }: AuthToggleProps) {
  const wrapperStyle: React.CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    backgroundColor: "var(--color-bg-default)",
    borderRadius: "var(--radius-full)",
    padding: "4px",
    boxShadow: "var(--shadow-sm)",
    border: "1px solid var(--color-border-default)",
    gap: "4px",
    animation: "fadeIn var(--transition-slow)",
  };

  const buttonStyle = (isActive: boolean): React.CSSProperties => ({
    border: "none",
    borderRadius: "var(--radius-full)",
    padding: "var(--space-2) var(--space-6)",
    fontSize: "var(--text-base)",
    fontWeight: 600,
    backgroundColor: isActive ? "var(--iu-crimson)" : "transparent",
    color: isActive ? "var(--color-text-inverse)" : "var(--color-text-secondary)",
    cursor: isActive ? "default" : "pointer",
    transition: "background-color var(--transition-base), color var(--transition-base)",
  });

  return (
    <div
      style={{
        width: "100%",
        display: "flex",
        justifyContent: "center",
        marginBottom: "var(--space-6)",
        marginTop: "var(--space-2)",
      }}
    >
      <div style={{ display: "flex", justifyContent: "center", width: width ? `${width}px` : "auto" }}>
        <div style={wrapperStyle}>
          <button
            type="button"
            style={buttonStyle(active === "login")}
          onClick={() => {
            if (active !== "login") {
              onSelectLogin?.();
            }
          }}
          onMouseEnter={(e) => {
            if (active === "login") return;
            e.currentTarget.style.backgroundColor = "var(--color-bg-hover)";
            e.currentTarget.style.color = "var(--color-text-primary)";
          }}
          onMouseLeave={(e) => {
            if (active === "login") return;
            e.currentTarget.style.backgroundColor = "transparent";
            e.currentTarget.style.color = "var(--color-text-secondary)";
          }}
        >
          Login
        </button>
        <button
          type="button"
          style={buttonStyle(active === "signup")}
          onClick={() => {
            if (active !== "signup") {
              onSelectSignup?.();
            }
          }}
          onMouseEnter={(e) => {
            if (active === "signup") return;
            e.currentTarget.style.backgroundColor = "var(--color-bg-hover)";
            e.currentTarget.style.color = "var(--color-text-primary)";
          }}
          onMouseLeave={(e) => {
            if (active === "signup") return;
            e.currentTarget.style.backgroundColor = "transparent";
            e.currentTarget.style.color = "var(--color-text-secondary)";
          }}
        >
          Sign Up
        </button>
      </div>
      </div>
    </div>
  );
}
