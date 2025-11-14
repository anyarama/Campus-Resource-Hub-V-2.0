import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';

interface CHDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title?: string;
  description?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
}

const maxWidthClasses: Record<NonNullable<CHDialogProps['maxWidth']>, string> = {
  sm: 'sm:max-w-sm',
  md: 'sm:max-w-md',
  lg: 'sm:max-w-lg',
  xl: 'sm:max-w-2xl',
  '2xl': 'sm:max-w-3xl',
};

export function CHDialog({
  open,
  onOpenChange,
  title,
  description,
  children,
  footer,
  maxWidth = 'md',
}: CHDialogProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  if (!mounted || !open) return null;

  const handleClose = () => onOpenChange(false);

  return createPortal(
    <>
      <div
        className="fixed inset-0 z-50 bg-brand-black/40"
        aria-hidden="true"
        onClick={handleClose}
      />
      <div className="fixed inset-0 z-50 flex items-center justify-center">
        <div
          className={`relative w-full max-w-[calc(100%-2rem)] ${maxWidthClasses[maxWidth]} bg-surface border border-border-default rounded-lg shadow-2xl flex flex-col gap-2 p-4`}
          role="dialog"
          aria-modal="true"
          aria-labelledby="ch-dialog-title"
          onClick={(e) => e.stopPropagation()}
          style={{ maxHeight: '70vh' }}
        >
          <button
            type="button"
            className="absolute top-4 right-4 p-2 rounded-md hover:bg-subtle transition-colors"
            aria-label="Close dialog"
            onClick={handleClose}
          >
            <X className="w-4 h-4 text-fg-muted" />
          </button>

          {(title || description) && (
            <div className="space-y-1 pr-8">
              {title && (
                <h2 id="ch-dialog-title" className="text-h4 text-fg-default">
                  {title}
                </h2>
              )}
              {description && (
                <p className="text-body text-fg-muted">{description}</p>
              )}
            </div>
          )}

          <div className="flex-1 overflow-y-auto">
            {children}
          </div>

          {footer && (
            <div className="sticky bottom-0 bg-surface pt-2 -mb-2 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end border-t border-border-muted">
              {footer}
            </div>
          )}
        </div>
      </div>
    </>,
    document.body
  );
}
