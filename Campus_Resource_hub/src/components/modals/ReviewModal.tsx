import React, { useState } from 'react';
import { X, Star } from 'lucide-react';
import { CHButton } from '../ui/ch-button';
import { toast } from 'sonner';
import { createReview } from '../../api/services/reviewsService';
import type { Resource } from '../../api/types';

interface ReviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  resource: Resource;
  onSuccess?: () => void;
}

export function ReviewModal({ isOpen, onClose, resource, onSuccess }: ReviewModalProps) {
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (rating === 0) {
      toast.error('Please select a rating');
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await createReview({
        resource_id: resource.id,
        rating,
        comment: comment.trim() || undefined,
      });

      if (response.error) {
        throw new Error(response.error);
      }

      toast.success('Review submitted successfully');
      setRating(0);
      setComment('');
      onSuccess?.();
      onClose();
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to submit review';
      toast.error('Error submitting review', {
        description: message,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-brand-black/40 z-50 animate-fade-in"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
          className="bg-surface rounded-lg shadow-lg w-full max-w-md animate-slide-in-up"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-default">
            <div>
              <h2 className="text-h3 text-fg-default">Write a Review</h2>
              <p className="text-micro text-fg-muted mt-1">{resource.name}</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-md hover:bg-subtle transition-colors"
            >
              <X className="w-5 h-5 text-fg-muted" />
            </button>
          </div>

          {/* Content */}
          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            {/* Star Rating */}
            <div>
              <label className="block text-caption-semibold text-fg-default mb-3">
                Your Rating *
              </label>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setRating(star)}
                    onMouseEnter={() => setHoverRating(star)}
                    onMouseLeave={() => setHoverRating(0)}
                    className="p-1 transition-transform hover:scale-110"
                  >
                    <Star
                      className={`w-8 h-8 ${
                        star <= (hoverRating || rating)
                          ? 'fill-amber-400 text-amber-400'
                          : 'text-neutral-300'
                      }`}
                    />
                  </button>
                ))}
              </div>
              {rating > 0 && (
                <p className="text-micro text-fg-muted mt-2">
                  {rating === 1 && 'Poor'}
                  {rating === 2 && 'Fair'}
                  {rating === 3 && 'Good'}
                  {rating === 4 && 'Very Good'}
                  {rating === 5 && 'Excellent'}
                </p>
              )}
            </div>

            {/* Comment */}
            <div>
              <label className="block text-caption-semibold text-fg-default mb-2">
                Your Review (Optional)
              </label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Share your experience with this resource..."
                rows={4}
                maxLength={500}
                className="w-full px-4 py-3 border border-default rounded-md 
                  text-caption text-fg-default placeholder:text-fg-muted
                  bg-surface focus:outline-none focus:ring-2 focus:ring-brand-crimson
                  resize-none"
              />
              <p className="text-micro text-fg-muted mt-1">
                {comment.length}/500 characters
              </p>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 border border-default rounded-md
                  text-caption-semibold text-fg-default
                  hover:bg-subtle transition-colors"
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={rating === 0 || isSubmitting}
                className="flex-1 px-4 py-2 bg-brand-crimson text-white rounded-md
                  text-caption-semibold hover:bg-brand-crimson-dark
                  disabled:opacity-50 disabled:cursor-not-allowed
                  transition-colors"
              >
                {isSubmitting ? 'Submitting...' : 'Submit Review'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}
