/**
 * Signup Page
 * Split-screen design with IU branding
 */

import React from 'react';
import { AuthLayout } from '../auth/AuthLayout';
import { SignUpCard } from '../auth/SignUpCard';
import { AuthToggle } from '../auth/AuthToggle';

interface SignupProps {
  onNavigateToLogin?: () => void;
}

export function Signup({ onNavigateToLogin }: SignupProps) {
  const handleSuccess = (data: { name: string; email: string; role: string }) => {
    console.log('Signup successful:', data);
    // AuthContext handles the navigation
  };

  return (
    <AuthLayout>
      <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <AuthToggle active="signup" onSelectLogin={onNavigateToLogin} width={520} />
        <SignUpCard
          onNavigateToLogin={onNavigateToLogin}
          onSuccess={handleSuccess}
        />
      </div>
    </AuthLayout>
  );
}
