import React, { useState, useEffect } from 'react';
import { X, MapPin, Users, DollarSign, Mail, Trash2, Edit, Calendar, Star, MessageSquare } from 'lucide-react';
import { CHButton } from '../ui/ch-button';
import { CHBadge } from '../ui/ch-badge';
import { deleteResource } from '../../api/services/resourcesService';
import { getResourceReviews } from '../../api/services/reviewsService';
import { toast } from 'sonner';
import type { Resource, Review } from '../../api/types';
import { useAuth } from '../../contexts/AuthContext';
import { BookingFormModal } from './BookingFormModal';
import { ReviewModal } from './ReviewModal';

/**
 * ResourceDetailModal
 * Shows full resource details with edit/delete actions
 */

interface ResourceDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  resource: Resource | null;
  onEdit: () => void;
  onDelete: () => void;
  onBookingSuccess?: () => void;
}

export function ResourceDetailModal({
  isOpen,
  onClose,
  resource,
  onEdit,
  onDelete,
  onBookingSuccess,
}: ResourceDetailModalProps) {
  const { user } = useAuth();
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [bookingModalOpen, setBookingModalOpen] = useState(false);
  const [reviewModalOpen, setReviewModalOpen] = useState(false);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [reviewsLoading, setReviewsLoading] = useState(false);
  const [avgRating, setAvgRating] = useState(0);
  
  // Fetch reviews when modal opens
  useEffect(() => {
    if (isOpen && resource) {
      fetchReviews();
    }
  }, [isOpen, resource?.id]);
  
  const fetchReviews = async () => {
    if (!resource) return;
    
    setReviewsLoading(true);
    const response = await getResourceReviews(resource.id);
    
    if (response.data) {
      setReviews(response.data.items);
      // Calculate average rating
      if (response.data.items.length > 0) {
        const sum = response.data.items.reduce((acc, review) => acc + review.rating, 0);
        setAvgRating(sum / response.data.items.length);
      } else {
        setAvgRating(0);
      }
    }
    setReviewsLoading(false);
  };
  
  if (!isOpen ||!resource) return null;
  
  const canEdit = user && (user.role === 'staff' || user.role === 'admin');
  const canDelete = user && user.role === 'admin';
  
  const handleDelete = async () => {
    if (!showDeleteConfirm) {
      setShowDeleteConfirm(true);
      return;
    }
    
    setIsDeleting(true);
    
    try {
      const response = await deleteResource(resource.id);
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      toast.success('Resource deleted successfully');
      onDelete();
      onClose();
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete resource';
      toast.error('Error deleting resource', {
        description: message,
      });
    } finally {
      setIsDeleting(false);
      setShowDeleteConfirm(false);
    }
  };
  
  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-brand-black/40 z-40 animate-fade-in"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 overflow-y-auto">
        <div
          className="bg-surface rounded-lg shadow-lg w-full max-w-3xl max-h-[90vh] overflow-y-auto animate-slide-in-up"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header with Image */}
          {resource.image_url && (
            <div className="relative h-64 bg-subtle">
              <img
                src={resource.image_url}
                alt={resource.name}
                className="w-full h-full object-cover"
              />
              <button
                onClick={onClose}
                className="absolute top-4 right-4 p-2 bg-white rounded-full shadow-md hover:bg-subtle"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          )}
          
          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Title and Status */}
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h2 className="text-h2 text-fg-default">{resource.name}</h2>
                  <CHBadge variant={resource.available ? 'success' : 'danger'}>
                    {resource.available ? 'Available' : 'Unavailable'}
                  </CHBadge>
                </div>
                <p className="text-caption text-fg-muted capitalize">
                  {resource.type}
                </p>
              </div>
              
              {!resource.image_url && (
                <button
                  onClick={onClose}
                  className="p-2 rounded-md hover:bg-subtle transition-colors"
                >
                  <X className="w-5 h-5 text-fg-muted" />
                </button>
              )}
            </div>
            
            {/* Description */}
            {resource.description && (
              <div>
                <h3 className="text-caption-semibold text-fg-default mb-2">Description</h3>
                <p className="text-caption text-fg-muted">{resource.description}</p>
              </div>
            )}
            
            {/* Details Grid */}
            <div className="grid grid-cols-2 gap-4">
              {/* Location */}
              <div className="flex items-start gap-3">
                <MapPin className="w-5 h-5 text-fg-muted flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-micro-semibold text-fg-muted uppercase tracking-wider mb-1">
                    Location
                  </p>
                  <p className="text-caption text-fg-default">{resource.location}</p>
                  {resource.building && (
                    <p className="text-micro text-fg-muted">{resource.building}</p>
                  )}
                  {resource.floor && (
                    <p className="text-micro text-fg-muted">Floor {resource.floor}</p>
                  )}
                </div>
              </div>
              
              {/* Capacity */}
              {resource.capacity && (
                <div className="flex items-start gap-3">
                  <Users className="w-5 h-5 text-fg-muted flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-micro-semibold text-fg-muted uppercase tracking-wider mb-1">
                      Capacity
                    </p>
                    <p className="text-caption text-fg-default">{resource.capacity} people</p>
                  </div>
                </div>
              )}
              
              {/* Hourly Rate */}
              {resource.hourly_rate && (
                <div className="flex items-start gap-3">
                  <DollarSign className="w-5 h-5 text-fg-muted flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-micro-semibold text-fg-muted uppercase tracking-wider mb-1">
                      Hourly Rate
                    </p>
                    <p className="text-caption text-fg-default">${resource.hourly_rate.toFixed(2)}/hour</p>
                  </div>
                </div>
              )}
              
              {/* Contact Email */}
              {resource.contact_email && (
                <div className="flex items-start gap-3">
                  <Mail className="w-5 h-5 text-fg-muted flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-micro-semibold text-fg-muted uppercase tracking-wider mb-1">
                      Contact
                    </p>
                    <p className="text-caption text-fg-default">{resource.contact_email}</p>
                  </div>
                </div>
              )}
            </div>
            
            {/* Amenities */}
            {resource.amenities && resource.amenities.length > 0 && (
              <div>
                <h3 className="text-caption-semibold text-fg-default mb-3">Amenities</h3>
                <div className="flex flex-wrap gap-2">
                  {resource.amenities.map((amenity, index) => (
                    <CHBadge key={index} variant="neutral">
                      {amenity}
                    </CHBadge>
                  ))}
                </div>
              </div>
            )}
            
            {/* Campus Info */}
            {resource.campus && (
              <div>
                <h3 className="text-caption-semibold text-fg-default mb-2">Campus</h3>
                <p className="text-caption text-fg-muted">{resource.campus}</p>
              </div>
            )}
            
            {/* Reviews Section */}
            <div className="border-t border-default pt-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-caption-semibold text-fg-default">Reviews</h3>
                  {avgRating > 0 && (
                    <div className="flex items-center gap-2 mt-1">
                      <div className="flex items-center">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <Star
                            key={star}
                            className={`w-4 h-4 ${
                              star <= Math.round(avgRating)
                                ? 'fill-amber-400 text-amber-400'
                                : 'text-neutral-300'
                            }`}
                          />
                        ))}
                      </div>
                      <span className="text-micro text-fg-muted">
                        {avgRating.toFixed(1)} ({reviews.length} {reviews.length === 1 ? 'review' : 'reviews'})
                      </span>
                    </div>
                  )}
                </div>
                <button
                  onClick={() => setReviewModalOpen(true)}
                  className="px-3 py-1.5 text-caption-semibold text-brand-crimson 
                    hover:bg-brand-crimson-light rounded-md transition-colors"
                >
                  <MessageSquare className="w-4 h-4 inline-block mr-1" />
                  Write Review
                </button>
              </div>
              
              {/* Reviews List */}
              {reviewsLoading ? (
                <div className="text-center py-4">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-iu-crimson mx-auto"></div>
                </div>
              ) : reviews.length > 0 ? (
                <div className="space-y-4 max-h-64 overflow-y-auto">
                  {reviews.slice(0, 5).map((review) => (
                    <div key={review.id} className="border-b border-default pb-4 last:border-0">
                      <div className="flex items-center gap-2 mb-2">
                        <div className="flex">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <Star
                              key={star}
                              className={`w-4 h-4 ${
                                star <= review.rating
                                  ? 'fill-amber-400 text-amber-400'
                                  : 'text-neutral-300'
                              }`}
                            />
                          ))}
                        </div>
                        <span className="text-micro text-fg-muted">
                          by {review.user?.full_name || review.user?.username || 'Anonymous'}
                        </span>
                        <span className="text-micro text-fg-muted">•</span>
                        <span className="text-micro text-fg-muted">
                          {new Date(review.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      {review.comment && (
                        <p className="text-caption text-fg-default">{review.comment}</p>
                      )}
                    </div>
                  ))}
                  {reviews.length > 5 && (
                    <p className="text-micro text-fg-muted text-center pt-2">
                      Showing 5 of {reviews.length} reviews
                    </p>
                  )}
                </div>
              ) : (
                <div className="text-center py-6">
                  <MessageSquare className="w-8 h-8 text-fg-muted mx-auto mb-2" />
                  <p className="text-caption text-fg-muted">No reviews yet</p>
                  <p className="text-micro text-fg-muted mt-1">Be the first to review this resource</p>
                </div>
              )}
            </div>
            
            {/* Delete Confirmation */}
            {showDeleteConfirm && (
              <div className="bg-accent-red-light border border-accent-red/20 rounded-md p-4">
                <p className="text-caption text-fg-default mb-2">
                  Are you sure you want to delete this resource? This action cannot be undone.
                </p>
                <div className="flex gap-2">
                  <CHButton
                    variant="secondary"
                    size="sm"
                    onClick={() => setShowDeleteConfirm(false)}
                  >
                    Cancel
                  </CHButton>
                  <CHButton
                    variant="danger"
                    size="sm"
                    onClick={handleDelete}
                    disabled={isDeleting}
                    loading={isDeleting}
                  >
                    Delete Resource
                  </CHButton>
                </div>
              </div>
            )}
            
            {/* Actions */}
            <div className="flex gap-3 pt-4 border-t border-default">
              {resource.available && (
                <CHButton
                  variant="primary"
                  className="flex-1"
                  onClick={() => setBookingModalOpen(true)}
                >
                  <Calendar className="w-4 h-4" />
                  Book Now
                </CHButton>
              )}
              
              {!resource.available && (
                <div className="flex-1 px-4 py-2 bg-subtle border border-default rounded-md text-center">
                  <p className="text-caption text-fg-muted">Resource unavailable for booking</p>
                </div>
              )}
              
              {canEdit && (
                <CHButton
                  variant="secondary"
                  onClick={onEdit}
                >
                  <Edit className="w-4 h-4" />
                  Edit
                </CHButton>
              )}
              
              {canDelete && !showDeleteConfirm && (
                <CHButton
                  variant="danger"
                  onClick={() => setShowDeleteConfirm(true)}
                >
                  <Trash2 className="w-4 h-4" />
                  Delete
                </CHButton>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* Booking Modal */}
      {resource && (
        <BookingFormModal
          isOpen={bookingModalOpen}
          onClose={() => setBookingModalOpen(false)}
          onSuccess={() => {
            setBookingModalOpen(false);
            if (onBookingSuccess) {
              onBookingSuccess();
            }
            toast.success('Booking request submitted successfully');
          }}
          resource={resource}
        />
      )}
      
      {/* Review Modal */}
      {resource && (
        <ReviewModal
          isOpen={reviewModalOpen}
          onClose={() => setReviewModalOpen(false)}
          resource={resource}
          onSuccess={() => {
            fetchReviews(); // Refresh reviews after submission
          }}
        />
      )}
    </>
  );
}
