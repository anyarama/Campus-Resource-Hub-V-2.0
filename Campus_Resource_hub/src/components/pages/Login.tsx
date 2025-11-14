/**
 * Login Page
 * Enterprise-grade authentication screen using shared AuthLayout + LoginCard
 */

import React from 'react';
import { AuthLayout } from '../auth/AuthLayout';
import { LoginCard } from '../auth/LoginCard';
import { AuthToggle } from '../auth/AuthToggle';

interface LoginProps {
  onNavigateToSignUp?: () => void;
}

export function Login({ onNavigateToSignUp }: LoginProps) {
  const handleLoginSuccess = (data: { email: string }) => {
    console.log('Login successful:', data.email);
  };

  return (
    <AuthLayout>
      <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <AuthToggle active="login" onSelectSignup={onNavigateToSignUp} width={480} />
        <LoginCard
          onNavigateToSignUp={onNavigateToSignUp}
          onSuccess={handleLoginSuccess}
        />
      </div>
    </AuthLayout>
  );
}
