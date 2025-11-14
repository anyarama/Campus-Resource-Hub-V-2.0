import React, { useState, useEffect } from 'react';
import { X, Calendar, Clock, Loader2, AlertCircle } from 'lucide-react';
import { CHButton } from '../ui/ch-button';
import { CHInput } from '../ui/ch-input';
import { toast } from 'sonner';
import { createBooking } from '../../api/services/bookingsService';
import type { Resource, BookingFormData } from '../../api/types';

/**
 * BookingFormModal
 * Modal for creating new bookings
 * Supports date/time selection with validation
 */

interface BookingFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  resource: Resource;
}

export function BookingFormModal({
  isOpen,
  onClose,
  onSuccess,
  resource,
}: BookingFormModalProps) {
  // Form state
  const [formData, setFormData] = useState<BookingFormData>({
    resource_id: resource.id,
    start_time: '',
    end_time: '',
    purpose: '',
    notes: '',
    attendees_count: undefined,
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      setFormData({
        resource_id: resource.id,
        start_time: '',
        end_time: '',
        purpose: '',
        notes: '',
        attendees_count: undefined,
      });
      setErrors({});
    }
  }, [isOpen, resource.id]);
  
  // Update resource_id when resource changes
  useEffect(() => {
    setFormData(prev => ({ ...prev, resource_id: resource.id }));
  }, [resource.id]);
  
  // Handle input changes
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;
    
    if (type === 'number') {
      setFormData({ ...formData, [name]: value ? Number(value) : undefined });
    } else {
      setFormData({ ...formData, [name]: value });
    }
    
    // Clear error for this field
    if (errors[name]) {
      setErrors({ ...errors, [name]: '' });
    }
  };
  
  // Get minimum datetime (now + 1 hour)
  const getMinDateTime = (): string => {
    const now = new Date();
    now.setHours(now.getHours() + 1);
    now.setMinutes(0, 0, 0);
    // Format: YYYY-MM-DDTHH:mm
    return now.toISOString().slice(0, 16);
  };
  
  // Calculate suggested end time (start + 2 hours)
  const getSuggestedEndTime = (startTime: string): string => {
    if (!startTime) return '';
    const start = new Date(startTime);
    start.setHours(start.getHours() + 2);
    return start.toISOString().slice(0, 16);
  };
  
  // Auto-fill end time when start time changes
  useEffect(() => {
    if (formData.start_time && !formData.end_time) {
      setFormData(prev => ({
        ...prev,
        end_time: getSuggestedEndTime(prev.start_time),
      }));
    }
  }, [formData.start_time]);
  
  // Validate form
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.start_time) {
      newErrors.start_time = 'Start time is required';
    }
    
    if (!formData.end_time) {
      newErrors.end_time = 'End time is required';
    }
    
    if (formData.start_time && formData.end_time) {
      const start = new Date(formData.start_time);
      const end = new Date(formData.end_time);
      const now = new Date();
      
      // Check if start is in the past
      if (start < now) {
        newErrors.start_time = 'Start time cannot be in the past';
      }
      
      // Check if end is before start
      if (end <= start) {
        newErrors.end_time = 'End time must be after start time';
      }
      
      // Check if booking is too long (max 8 hours)
      const durationHours = (end.getTime() - start.getTime()) / (1000 * 60 * 60);
      if (durationHours > 8) {
        newErrors.end_time = 'Booking cannot exceed 8 hours';
      }
      
      // Check if booking is too short (min 30 minutes)
      if (durationHours < 0.5) {
        newErrors.end_time = 'Booking must be at least 30 minutes';
      }
    }
    
    if (formData.attendees_count && formData.attendees_count < 1) {
      newErrors.attendees_count = 'Number of attendees must be at least 1';
    }
    
    if (resource.capacity && formData.attendees_count && formData.attendees_count > resource.capacity) {
      newErrors.attendees_count = `Cannot exceed room capacity of ${resource.capacity}`;
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  // Calculate booking duration
  const getBookingDuration = (): string => {
    if (!formData.start_time || !formData.end_time) return '';
    
    const start = new Date(formData.start_time);
    const end = new Date(formData.end_time);
    const durationMs = end.getTime() - start.getTime();
    const hours = Math.floor(durationMs / (1000 * 60 * 60));
    const minutes = Math.floor((durationMs % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours === 0) {
      return `${minutes} minutes`;
    } else if (minutes === 0) {
      return `${hours} hour${hours > 1 ? 's' : ''}`;
    } else {
      return `${hours} hour${hours > 1 ? 's' : ''} ${minutes} min`;
    }
  };
  
  // Calculate total cost
  const getTotalCost = (): number | null => {
    if (!resource.hourly_rate || !formData.start_time || !formData.end_time) {
      return null;
    }
    
    const start = new Date(formData.start_time);
    const end = new Date(formData.end_time);
    const durationHours = (end.getTime() - start.getTime()) / (1000 * 60 * 60);
    
    return resource.hourly_rate * durationHours;
  };
  
  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      toast.error('Please fix the errors in the form');
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      // Convert datetime-local to ISO string for API
      const submitData: BookingFormData = {
        ...formData,
        start_time: new Date(formData.start_time).toISOString(),
        end_time: new Date(formData.end_time).toISOString(),
      };
      
      const response = await createBooking(submitData);
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      toast.success('Booking request submitted', {
        description: 'Your booking has been submitted for approval',
      });
      
      onSuccess();
      onClose();
      
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create booking';
      toast.error('Error creating booking', {
        description: message,
      });
    } finally {
      setIsSubmitting(false);
    }
  };
  
  if (!isOpen) return null;
  
  const duration = getBookingDuration();
  const totalCost = getTotalCost();
  
  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-brand-black/40 z-40 animate-fade-in"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
          className="bg-surface rounded-lg shadow-lg w-full max-w-2xl max-h-[85vh] flex flex-col animate-slide-in-up"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-default sticky top-0 bg-surface z-10">
            <div>
              <h2 className="text-h3 text-fg-default mb-1">Book Resource</h2>
              <p className="text-caption text-fg-muted">{resource.name}</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-md hover:bg-subtle transition-colors"
              disabled={isSubmitting}
            >
              <X className="w-5 h-5 text-fg-muted" />
            </button>
          </div>
          
          {/* Form - Scrollable Content */}
          <form onSubmit={handleSubmit} className="flex flex-col flex-1 min-h-0">
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {/* Resource Info Banner */}
              <div className="bg-subtle rounded-lg p-4 border border-default">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 bg-brand-crimson/10 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Calendar className="w-5 h-5 text-brand-crimson" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-caption-semibold text-fg-default mb-1">
                      {resource.name}
                    </h4>
                    <p className="text-caption text-fg-muted">
                      {resource.location}
                    </p>
                    {resource.capacity && (
                      <p className="text-caption text-fg-muted">
                        Capacity: {resource.capacity} people
                      </p>
                    )}
                  </div>
                </div>
              </div>
              
              {/* Divider */}
              <div className="h-px bg-default" />
              
              {/* Date & Time Section */}
              <div className="space-y-3">
                <h3 className="text-caption-semibold text-fg-default uppercase tracking-wide text-xs">
                  Date & Time
                </h3>
                
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1.5">
                    <label htmlFor="start_time" className="block text-caption-semibold text-fg-default">
                      Start Time *
                    </label>
                    <input
                      id="start_time"
                      name="start_time"
                      type="datetime-local"
                      value={formData.start_time}
                      onChange={handleChange}
                      min={getMinDateTime()}
                      required
                      className={`
                        h-10 px-3 py-2 w-full
                        bg-surface border rounded-md
                        text-caption text-fg-default
                        focus:outline-none focus:ring-2 focus:ring-brand-crimson focus:border-transparent
                        transition-all
                        ${errors.start_time ? 'border-red-500' : 'border-default'}
                      `}
                    />
                    {errors.start_time && (
                      <p className="text-micro text-red-600 flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" />
                        {errors.start_time}
                      </p>
                    )}
                  </div>
                  
                  <div className="space-y-1.5">
                    <label htmlFor="end_time" className="block text-caption-semibold text-fg-default">
                      End Time *
                    </label>
                    <input
                      id="end_time"
                      name="end_time"
                      type="datetime-local"
                      value={formData.end_time}
                      onChange={handleChange}
                      min={formData.start_time || getMinDateTime()}
                      required
                      className={`
                        h-10 px-3 py-2 w-full
                        bg-surface border rounded-md
                        text-caption text-fg-default
                        focus:outline-none focus:ring-2 focus:ring-brand-crimson focus:border-transparent
                        transition-all
                        ${errors.end_time ? 'border-red-500' : 'border-default'}
                      `}
                    />
                    {errors.end_time && (
                      <p className="text-micro text-red-600 flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" />
                        {errors.end_time}
                      </p>
                    )}
                  </div>
                </div>
                
                {/* Duration & Cost Display */}
                {duration && (
                  <div className="bg-subtle rounded-lg p-3 border border-default">
                    <div className="flex items-center justify-between text-caption">
                      <div className="flex items-center gap-2 text-fg-muted">
                        <Clock className="w-4 h-4" />
                        <span>Duration: <strong className="text-fg-default">{duration}</strong></span>
                      </div>
                      
                      {totalCost !== null && (
                        <div className="text-fg-muted">
                          Total Cost: <strong className="text-brand-crimson">${totalCost.toFixed(2)}</strong>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
              
              {/* Divider */}
              <div className="h-px bg-default" />
              
              {/* Booking Details Section */}
              <div className="space-y-3">
                <h3 className="text-caption-semibold text-fg-default uppercase tracking-wide text-xs">
                  Booking Details
                </h3>
                
                {resource.capacity && (
                  <div className="space-y-1.5">
                    <label htmlFor="attendees_count" className="block text-caption-semibold text-fg-default">
                      Number of Attendees
                    </label>
                    <CHInput
                      id="attendees_count"
                      name="attendees_count"
                      type="number"
                      placeholder={`e.g., 1-${resource.capacity}`}
                      value={formData.attendees_count?.toString() || ''}
                      onChange={handleChange}
                      error={errors.attendees_count}
                      min="1"
                      max={resource.capacity}
                    />
                  </div>
                )}
                
                <div className="space-y-1.5">
                  <label htmlFor="purpose" className="block text-caption-semibold text-fg-default">
                    Purpose
                  </label>
                  <textarea
                    id="purpose"
                    name="purpose"
                    placeholder="What is this booking for? (e.g., Group study session, Team meeting)"
                    value={formData.purpose}
                    onChange={handleChange}
                    rows={2}
                    className="w-full px-3 py-2 bg-surface border border-default rounded-md text-caption text-fg-default resize-none focus:outline-none focus:ring-2 focus:ring-brand-crimson focus:border-transparent transition-all"
                  />
                </div>
                
                <div className="space-y-1.5">
                  <label htmlFor="notes" className="block text-caption-semibold text-fg-default">
                    Additional Notes
                  </label>
                  <textarea
                    id="notes"
                    name="notes"
                    placeholder="Any special requirements or notes for the resource manager"
                    value={formData.notes}
                    onChange={handleChange}
                    rows={2}
                    className="w-full px-3 py-2 bg-surface border border-default rounded-md text-caption text-fg-default resize-none focus:outline-none focus:ring-2 focus:ring-brand-crimson focus:border-transparent transition-all"
                  />
                </div>
              </div>
              
              {/* Policy Notice */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <h4 className="text-caption-semibold text-blue-900 mb-1">
                      Booking Policy
                    </h4>
                    <ul className="text-caption text-blue-800 space-y-1">
                      <li>• Your booking request will be reviewed by the resource manager</li>
                      <li>• You can cancel up to 2 hours before the start time</li>
                      <li>• Please arrive on time and notify us if you need to cancel</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Actions - Fixed at bottom */}
            <div className="border-t border-default p-4">
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={onClose}
                  disabled={isSubmitting}
                  className="flex-1 h-10 px-4 rounded-md bg-surface border border-default text-fg-default hover:bg-subtle transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="flex-1 h-10 px-4 rounded-md bg-brand-crimson text-white hover:bg-brand-crimson/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
                  Submit Booking Request
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}
