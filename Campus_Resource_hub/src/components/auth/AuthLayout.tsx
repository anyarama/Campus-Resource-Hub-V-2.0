/**
 * @component AuthLayout
 * @description Enterprise-grade IU-branded authentication layout
 */

import { ReactNode, useState } from "react";

interface AuthLayoutProps {
  children: ReactNode;
  showSuccessToast?: boolean;
  successMessage?: string;
}

export function AuthLayout({ children, showSuccessToast, successMessage }: AuthLayoutProps) {
  const bgImages = [
    "/login_images/20250805_CampusScenics_JB_0030.jpg",
    "/login_images/20250805_CampusScenics_JB_0093.jpg",
    "/login_images/20250805_CampusScenics_JB_0149.jpg",
    "/login_images/20250805_CampusScenics_JB_0160.jpg",
  ];

  const [bgImage] = useState(() => bgImages[Math.floor(Math.random() * bgImages.length)]);

  return (
    <div
      style={{
        minHeight: "100vh",
        width: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "var(--iu-cream-dark)",
        padding: "var(--space-8)",
      }}
    >
      <div
        style={{
          display: "flex",
          overflow: "hidden",
          width: "1440px",
          height: "1024px",
          borderRadius: "var(--radius-xl)",
          boxShadow: "var(--shadow-xl)",
          backgroundColor: "var(--color-bg-default)",
        }}
      >
        <div
          style={{
            position: "relative",
            width: "480px",
            height: "100%",
            backgroundColor: "var(--iu-crimson-light)",
            overflow: "hidden",
            backgroundImage:
              "linear-gradient(180deg, rgba(255,255,255,0.08) 0%, transparent 40%), linear-gradient(120deg, rgba(255,255,255,0.12) 0%, transparent 55%)",
            backgroundBlendMode: "screen",
          }}
        >
          <div
            style={{
              position: "absolute",
              inset: 0,
            }}
          >
            <img
              src={bgImage}
              alt="Indiana University Campus"
              style={{ width: "100%", height: "100%", objectFit: "cover", opacity: 0.15, filter: "brightness(1.15) saturate(0.8)" }}
              onError={(e) => {
                // eslint-disable-next-line no-console
                console.error("Image failed to load:", bgImage);
                e.currentTarget.style.display = "none";
              }}
            />
          </div>

          <div
            style={{
              position: "absolute",
              inset: 0,
              background: "radial-gradient(circle at 25% 25%, rgba(255, 255, 255, 0.6), transparent 60%)",
              mixBlendMode: "screen",
              opacity: 0.6,
            }}
          />

          <div
            style={{
              position: "absolute",
              inset: 0,
              background:
                "linear-gradient(150deg, rgba(153, 0, 0, 0.35) 0%, rgba(153, 0, 0, 0.3) 45%, rgba(74, 0, 0, 0.5) 100%)",
            }}
          />

          <div
            style={{
              position: "relative",
              zIndex: 1,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              height: "100%",
              padding: "var(--space-16)",
              textAlign: "center",
            }}
          >
            <div
              style={{
                marginBottom: "var(--space-6)",
                animation: "fadeIn var(--transition-slower) ease-out",
              }}
            >
              <img
                src="/login_images/Indiana_Hoosiers_logo.svg.png"
                alt="Indiana Hoosiers"
                style={{
                  width: "80px",
                  height: "auto",
                  filter: "drop-shadow(0 2px 8px rgba(0, 0, 0, 0.2))",
                }}
              />
            </div>

            <p
              style={{
                color: "rgba(255, 255, 255, 0.95)",
                fontSize: "var(--text-base)",
                letterSpacing: "var(--letter-spacing-wide)",
                textTransform: "uppercase",
                marginBottom: "var(--space-4)",
                fontWeight: 600,
                animation: "fadeIn var(--transition-slower) 120ms ease-out",
              }}
            >
              Indiana University
            </p>

            <h2
              style={{
                color: "white",
                fontSize: "var(--text-3xl)",
                fontWeight: 600,
                lineHeight: "var(--line-height-normal)",
                letterSpacing: "var(--letter-spacing-tight)",
                maxWidth: "360px",
                textShadow: "0 2px 16px rgba(0, 0, 0, 0.18)",
                animation: "fadeIn var(--transition-slower) 220ms ease-out",
              }}
            >
              Campus Resource Hub
            </h2>

            <p
              style={{
                color: "rgba(255, 255, 255, 0.85)",
                fontSize: "var(--text-md)",
                marginTop: "var(--space-3)",
                lineHeight: "var(--line-height-relaxed)",
                maxWidth: "360px",
                animation: "fadeIn var(--transition-slower) 320ms ease-out",
              }}
            >
              Streamline campus resource booking and management
            </p>
          </div>
        </div>

        <div
          style={{
            position: "relative",
            flex: 1,
            height: "100%",
            backgroundColor: "var(--iu-cream)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "var(--space-8)",
          }}
        >
          {showSuccessToast && (
            <div
              style={{
                position: "absolute",
                top: "var(--space-8)",
                left: "50%",
                transform: "translateX(-50%)",
                zIndex: 10,
                minWidth: "380px",
                maxWidth: "500px",
                animation: "slideDown var(--transition-slow)",
                backgroundColor: "var(--color-bg-default)",
                borderRadius: "var(--radius-md)",
                boxShadow: "var(--shadow-xl)",
                padding: "var(--space-4)",
                borderLeft: "4px solid var(--color-success)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)" }}>
                <div
                  style={{
                    width: "40px",
                    height: "40px",
                    borderRadius: "var(--radius-full)",
                    backgroundColor: "var(--color-bg-success)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                  }}
                >
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path
                      d="M16.6667 5L7.5 14.1667L3.33334 10"
                      stroke="var(--color-success)"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </div>
                <div style={{ flex: 1 }}>
                  <p
                    style={{
                      fontSize: "var(--text-md)",
                      fontWeight: 600,
                      color: "var(--color-text-primary)",
                      marginBottom: "var(--space-1)",
                    }}
                  >
                    {successMessage || "Authentication Successful"}
                  </p>
                  <p
                    style={{
                      fontSize: "var(--text-base)",
                      color: "var(--color-text-secondary)",
                    }}
                  >
                    Redirecting to your dashboard...
                  </p>
                </div>
              </div>
            </div>
          )}

          <div style={{ width: "100%", maxWidth: "600px" }}>{children}</div>
        </div>
      </div>
    </div>
  );
}
