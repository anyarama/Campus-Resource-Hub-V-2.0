/**
 * @component LoginCard
 * @description Enterprise-grade login form aligned with reference design system
 */

import React, { useState, FormEvent } from "react";
import { Checkbox } from "../ui/checkbox";
import { EmailInput } from "./inputs/EmailInput";
import { PasswordInput } from "./inputs/PasswordInput";
import { AuthPrimaryButton } from "./buttons/AuthPrimaryButton";
import { InlineLink } from "./links/InlineLink";
import { FormFeedbackAlert } from "./alerts/FormFeedbackAlert";
import { useAuth } from "../../contexts/AuthContext";

interface LoginCardProps {
  onNavigateToSignUp?: () => void;
  onSuccess?: (data: { email: string }) => void;
}

export function LoginCard({ onNavigateToSignUp, onSuccess }: LoginCardProps) {
  const { login, error, loading, clearError } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [emailError, setEmailError] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearError();

    if (!email.includes("@iu.edu")) {
      setEmailError(true);
      return;
    }

    if (!password || password.trim().length === 0) {
      setEmailError(false);
      return;
    }

    setEmailError(false);

    const success = await login({
      email,
      password,
      remember_me: rememberMe,
    });

    if (success) {
      setIsSuccess(true);
      setTimeout(() => {
        onSuccess?.({ email });
      }, 500);
    }
  };

  const hasError = Boolean(error) || emailError;
  const errorMessage = emailError ? "Please use your IU email address (@iu.edu)" : error;

  const handleDismissError = () => {
    if (emailError) {
      setEmailError(false);
    }
    if (error) {
      clearError();
    }
  };

  return (
    <div
      style={{
        width: "480px",
        minHeight: "520px",
        borderRadius: "var(--radius-lg)",
        backgroundColor: "var(--color-bg-default)",
        padding: "var(--space-8)",
        boxShadow: "var(--shadow-md)",
        animation: "fadeInScale var(--transition-slow)",
      }}
    >
      <div style={{ marginBottom: "var(--space-8)" }}>
        <h2
          style={{
            fontSize: "var(--text-2xl)",
            fontWeight: 600,
            color: "var(--color-text-primary)",
            marginBottom: "var(--space-2)",
            letterSpacing: "var(--letter-spacing-tight)",
          }}
        >
          Welcome Back
        </h2>
        <p
          style={{
            fontSize: "var(--text-md)",
            color: "var(--color-text-secondary)",
            lineHeight: "var(--line-height-relaxed)",
          }}
        >
          Sign in to access your campus resources and bookings.
        </p>
      </div>

      {hasError && (
        <div style={{ marginBottom: "var(--space-4)" }}>
          <FormFeedbackAlert variant="error" dismissible onDismiss={handleDismissError}>
            {errorMessage}
          </FormFeedbackAlert>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
          <EmailInput
            value={email}
            onChange={setEmail}
            error={emailError}
            disabled={loading || isSuccess}
            required
            showValidation
          />

          <PasswordInput value={password} onChange={setPassword} disabled={loading || isSuccess} required />
        </div>

        <div
          style={{
            marginTop: "var(--space-4)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
            <Checkbox
              id="remember"
              disabled={loading || isSuccess}
              checked={rememberMe}
              onCheckedChange={(checked) => setRememberMe(checked === true)}
              style={{
                borderColor: "var(--color-border-default)",
                borderRadius: "var(--radius-sm)",
                backgroundColor: "var(--color-bg-default)",
              }}
            />
            <label
              htmlFor="remember"
              style={{
                fontSize: "var(--text-base)",
                color: "var(--color-text-secondary)",
                cursor: "pointer",
                userSelect: "none",
              }}
            >
              Remember me
            </label>
          </div>
          <InlineLink href="#" variant="primary">
            Forgot password?
          </InlineLink>
        </div>

        <div style={{ marginTop: "var(--space-6)" }}>
          <AuthPrimaryButton
            type="submit"
            isLoading={loading}
            isSuccess={isSuccess}
            disabled={loading || isSuccess}
            loadingText="Signing in..."
            successText="Welcome!"
          >
            Sign In
          </AuthPrimaryButton>
        </div>

        <div style={{ marginTop: "var(--space-4)", textAlign: "center" }}>
          <span style={{ fontSize: "var(--text-base)", color: "var(--color-text-secondary)" }}>
            Don't have an account?{" "}
          </span>
          <InlineLink
            href="#"
            variant="primary"
            onClick={(e) => {
              e.preventDefault();
              onNavigateToSignUp?.();
            }}
          >
            Create one
          </InlineLink>
        </div>
      </form>
    </div>
  );
}
