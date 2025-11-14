import React, { useState, useEffect } from 'react';
import { 
  Calendar,
  Clock,
  MapPin,
  MessageSquare,
  X,
  AlertCircle,
  BookOpen,
  CheckCircle,
  XCircle,
  Loader2
} from 'lucide-react';
import { toast } from 'sonner';
import { getMyBookings, cancelBooking } from '../../api/services/bookingsService';
import type { Booking } from '../../api/types';
import { CHButton } from '../ui/ch-button';
import { CHBadge } from '../ui/ch-badge';
import { CHTabs, CHTabsContent } from '../ui/ch-tabs';
import { CHCard, CHCardContent } from '../ui/ch-card';
import { CHEmpty } from '../ui/ch-empty';
import { BookingFormModal } from '../modals/BookingFormModal';

/**
 * My Bookings Page
 * Clean tabbed interface with booking cards and actions
 * Tabs: Upcoming, Pending, Past, Cancelled/Rejected
 */

export function MyBookings() {
  const [activeTab, setActiveTab] = useState('upcoming');
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Modal states
  const [cancelConfirmId, setCancelConfirmId] = useState<number | null>(null);
  const [rebookModalOpen, setRebookModalOpen] = useState(false);
  const [rebookResource, setRebookResource] = useState<any>(null);
  
  // Fetch bookings from API
  useEffect(() => {
    fetchBookings();
  }, []);
  
  const fetchBookings = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await getMyBookings();
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      if (response.data) {
        setBookings(response.data.items || []);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load bookings';
      setError(errorMessage);
      toast.error('Error loading bookings', {
        description: errorMessage,
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Format date for display
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    // Check if today
    if (date.toDateString() === today.toDateString()) {
      return `Today, ${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
    }
    
    // Check if tomorrow
    if (date.toDateString() === tomorrow.toDateString()) {
      return `Tomorrow, ${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
    }
    
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };
  
  // Format time range for display
  const formatTimeRange = (startString: string, endString: string): string => {
    const start = new Date(startString);
    const end = new Date(endString);
    
    const startTime = start.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
    const endTime = end.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
    
    return `${startTime} - ${endTime}`;
  };
  
  // Calculate duration
  const getDuration = (startString: string, endString: string): string => {
    const start = new Date(startString);
    const end = new Date(endString);
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
  
  // Check if booking can be cancelled (more than 2 hours before start)
  const canCancel = (startTime: string): boolean => {
    const start = new Date(startTime);
    const now = new Date();
    const hoursUntilStart = (start.getTime() - now.getTime()) / (1000 * 60 * 60);
    return hoursUntilStart > 2;
  };
  
  // Filter bookings by status
  const getBookingsByStatus = () => {
    const now = new Date();
    
    const upcoming = bookings.filter(b => 
      b.status === 'confirmed' && new Date(b.start_time) > now
    );
    
    const pending = bookings.filter(b => 
      b.status === 'pending'
    );
    
    const past = bookings.filter(b => 
      (b.status === 'completed' || (b.status === 'confirmed' && new Date(b.end_time) < now))
    );
    
    const cancelled = bookings.filter(b => 
      b.status === 'cancelled'
    );
    
    return { upcoming, pending, past, cancelled };
  };
  
  const { upcoming: upcomingBookings, pending: pendingBookings, past: pastBookings, cancelled: cancelledRejectedBookings } = getBookingsByStatus();
  
  // Handle message - navigate to messages
  const handleMessage = (booking: Booking) => {
    // TODO: Navigate to messages page when implemented
    if (booking.resource?.contact_email) {
      toast.info('Messaging feature coming soon', {
        description: `Contact: ${booking.resource.contact_email}`
      });
    } else {
      toast.info('Contact information not available');
    }
  };
  
  // Handle cancel booking
  const handleCancelRequest = (bookingId: number, startTime: string) => {
    if (!canCancel(startTime)) {
      toast.error('Cannot cancel booking', {
        description: 'Bookings can only be cancelled up to 2 hours before the start time',
      });
      return;
    }
    setCancelConfirmId(bookingId);
  };
  
  const handleCancelConfirm = async () => {
    if (!cancelConfirmId) return;
    
    try {
      const response = await cancelBooking(cancelConfirmId);
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      toast.success('Booking cancelled successfully');
      setCancelConfirmId(null);
      
      // Refresh bookings
      fetchBookings();
      
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to cancel booking';
      toast.error('Error cancelling booking', {
        description: message,
      });
    }
  };
  
  // Handle rebook
  const handleRebook = (booking: Booking) => {
    if (booking.resource) {
      setRebookResource(booking.resource);
      setRebookModalOpen(true);
    } else {
      toast.error('Resource information not available');
    }
  };
  
  // Render booking card
  const renderBookingCard = (booking: Booking, showActions: 'upcoming' | 'pending' | 'past' | 'cancelled') => {
    const resourceName = booking.resource?.name || 'Unknown Resource';
    const location = booking.resource?.location || 'Location not specified';
    
    return (
      <CHCard key={booking.id} elevation="sm">
        <CHCardContent>
          <div className="flex flex-col gap-4">
            {/* Main Content Row */}
            <div className="flex items-start justify-between gap-6">
              {/* Left: Booking Details */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-3">
                  <h3 className="text-caption-semibold text-fg-default">
                    {resourceName}
                  </h3>
                  {showActions === 'pending' && (
                    <CHBadge variant="warning">Pending Approval</CHBadge>
                  )}
                  {showActions === 'past' && (
                    <CHBadge variant="neutral">Completed</CHBadge>
                  )}
                  {showActions === 'cancelled' && (
                    <CHBadge variant="danger">
                      {booking.status === 'cancelled' ? 'Cancelled' : 'Rejected'}
                    </CHBadge>
                  )}
                </div>
                
                <div className="flex flex-col gap-2">
                  {/* Location */}
                  <div className="flex items-center gap-2 text-caption text-fg-muted">
                    <MapPin className="w-4 h-4 flex-shrink-0" />
                    <span>{location}</span>
                  </div>
                  
                  {/* Date */}
                  <div className="flex items-center gap-2 text-caption text-fg-muted">
                    <Calendar className="w-4 h-4 flex-shrink-0" />
                    <span>{formatDate(booking.start_time)}</span>
                  </div>
                  
                  {/* Time + Duration */}
                  <div className="flex items-center gap-2 text-caption text-fg-muted">
                    <Clock className="w-4 h-4 flex-shrink-0" />
                    <span>
                      {formatTimeRange(booking.start_time, booking.end_time)} ({getDuration(booking.start_time, booking.end_time)})
                    </span>
                  </div>
                </div>
              </div>
              
              {/* Right: Actions */}
              <div className="flex items-start gap-2 flex-shrink-0">
                {(showActions === 'upcoming' || showActions === 'pending') && (
                  <>
                    <CHButton
                      variant="secondary"
                      size="sm"
                      onClick={() => handleMessage(booking)}
                    >
                      <MessageSquare className="w-4 h-4" />
                      Message
                    </CHButton>
                    
                    <CHButton
                      variant="danger"
                      size="sm"
                      onClick={() => handleCancelRequest(booking.id, booking.start_time)}
                    >
                      <X className="w-4 h-4" />
                      Cancel
                    </CHButton>
                  </>
                )}
                
                {(showActions === 'past' || showActions === 'cancelled') && (
                  <CHButton
                    variant="secondary"
                    size="sm"
                    onClick={() => handleRebook(booking)}
                  >
                    <Calendar className="w-4 h-4" />
                    Book Again
                  </CHButton>
                )}
              </div>
            </div>
            
            {/* Footer with Policy/Notes */}
            {booking.purpose && (
              <div className="flex items-start gap-2 pt-3 border-t border-muted">
                <AlertCircle className="w-4 h-4 text-fg-muted flex-shrink-0 mt-0.5" />
                <p className="text-caption text-fg-muted">
                  <strong>Purpose:</strong> {booking.purpose}
                </p>
              </div>
            )}
          </div>
        </CHCardContent>
      </CHCard>
    );
  };
  
  // Loading state
  if (isLoading) {
    return (
      <div className="flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-h1 mb-1">My Bookings</h1>
            <p className="text-caption text-fg-muted">
              View and manage all your resource bookings
            </p>
          </div>
        </div>
        
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin text-brand-crimson mx-auto mb-2" />
            <p className="text-caption text-fg-muted">Loading bookings...</p>
          </div>
        </div>
      </div>
    );
  }
  
  // Error state
  if (error) {
    return (
      <div className="flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-h1 mb-1">My Bookings</h1>
            <p className="text-caption text-fg-muted">
              View and manage all your resource bookings
            </p>
          </div>
        </div>
        
        <div className="flex items-center justify-center h-96">
          <div className="text-center max-w-md">
            <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <AlertCircle className="w-8 h-8 text-red-600" />
            </div>
            <h3 className="text-h3 mb-2">Failed to Load Bookings</h3>
            <p className="text-caption text-fg-muted mb-4">{error}</p>
            <CHButton
              variant="primary"
              onClick={fetchBookings}
            >
              Try Again
            </CHButton>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="flex flex-col gap-6">
      {/* Header Row */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-h1 mb-1">My Bookings</h1>
          <p className="text-caption text-fg-muted">
            View and manage all your resource bookings
          </p>
        </div>
      </div>
      
      {/* Sticky Tabs */}
      <div className="sticky top-0 z-10 bg-canvas pt-2 pb-4 -mx-6 px-6">
        <CHTabs
          tabs={[
            { value: 'upcoming', label: 'Upcoming', count: upcomingBookings.length },
            { value: 'pending', label: 'Pending', count: pendingBookings.length },
            { value: 'past', label: 'Past', count: pastBookings.length },
            { value: 'cancelled', label: 'Cancelled/Rejected', count: cancelledRejectedBookings.length },
          ]}
          value={activeTab}
          onValueChange={setActiveTab}
        >
          {/* Upcoming Tab */}
          <CHTabsContent value="upcoming" activeValue={activeTab}>
            {upcomingBookings.length === 0 ? (
              <CHEmpty
                icon={<Calendar className="w-8 h-8 text-fg-muted" />}
                title="No upcoming bookings"
                description="You don't have any upcoming bookings scheduled. Browse resources to make a new booking."
              />
            ) : (
              <div className="flex flex-col gap-4">
                {upcomingBookings.map((booking) => renderBookingCard(booking, 'upcoming'))}
              </div>
            )}
          </CHTabsContent>
          
          {/* Pending Tab */}
          <CHTabsContent value="pending" activeValue={activeTab}>
            {pendingBookings.length === 0 ? (
              <CHEmpty
                icon={<Clock className="w-8 h-8 text-fg-muted" />}
                title="No pending bookings"
                description="You don't have any bookings awaiting approval."
              />
            ) : (
              <div className="flex flex-col gap-4">
                {pendingBookings.map((booking) => renderBookingCard(booking, 'pending'))}
              </div>
            )}
          </CHTabsContent>
          
          {/* Past Tab */}
          <CHTabsContent value="past" activeValue={activeTab}>
            {pastBookings.length === 0 ? (
              <CHEmpty
                icon={<CheckCircle className="w-8 h-8 text-fg-muted" />}
                title="No past bookings"
                description="You haven't completed any bookings yet."
              />
            ) : (
              <div className="flex flex-col gap-4">
                {pastBookings.map((booking) => renderBookingCard(booking, 'past'))}
              </div>
            )}
          </CHTabsContent>
          
          {/* Cancelled/Rejected Tab */}
          <CHTabsContent value="cancelled" activeValue={activeTab}>
            {cancelledRejectedBookings.length === 0 ? (
              <CHEmpty
                icon={<XCircle className="w-8 h-8 text-fg-muted" />}
                title="No cancelled or rejected bookings"
                description="You don't have any cancelled or rejected bookings."
              />
            ) : (
              <div className="flex flex-col gap-4">
                {cancelledRejectedBookings.map((booking) => renderBookingCard(booking, 'cancelled'))}
              </div>
            )}
          </CHTabsContent>
        </CHTabs>
      </div>
      
      {/* Cancel Confirmation Modal */}
      {cancelConfirmId && (
        <>
          <div
            className="fixed inset-0 bg-brand-black/40 z-40 animate-fade-in"
            onClick={() => setCancelConfirmId(null)}
          />
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div
              className="bg-surface rounded-lg shadow-lg w-full max-w-md p-6 animate-slide-in-up"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-start gap-4 mb-6">
                <div className="w-12 h-12 bg-red-50 rounded-full flex items-center justify-center flex-shrink-0">
                  <AlertCircle className="w-6 h-6 text-red-600" />
                </div>
                <div>
                  <h3 className="text-h3 text-fg-default mb-2">Cancel Booking?</h3>
                  <p className="text-caption text-fg-muted">
                    Are you sure you want to cancel this booking? This action cannot be undone.
                  </p>
                </div>
              </div>
              
              <div className="flex gap-3">
                <CHButton
                  variant="secondary"
                  className="flex-1"
                  onClick={() => setCancelConfirmId(null)}
                >
                  Keep Booking
                </CHButton>
                <CHButton
                  variant="danger"
                  className="flex-1"
                  onClick={handleCancelConfirm}
                >
                  Cancel Booking
                </CHButton>
              </div>
            </div>
          </div>
        </>
      )}
      
      {/* Rebook Modal */}
      {rebookResource && (
        <BookingFormModal
          isOpen={rebookModalOpen}
          onClose={() => {
            setRebookModalOpen(false);
            setRebookResource(null);
          }}
          onSuccess={() => {
            fetchBookings();
            setRebookResource(null);
          }}
          resource={rebookResource}
        />
      )}
    </div>
  );
}
