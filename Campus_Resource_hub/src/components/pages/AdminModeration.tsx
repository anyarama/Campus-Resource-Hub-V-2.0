import React, { useState, useEffect } from 'react';
import { 
  CheckCircle, 
  MoreVertical,
  AlertTriangle,
  Filter
} from 'lucide-react';
import { toast } from 'sonner';
import { getFlaggedReviews, hideReview } from '../../api/services/adminService';
import type { Review } from '../../api/types';
import { CHButton } from '../ui/ch-button';
import { CHBadge } from '../ui/ch-badge';
import { CHCard, CHCardContent, CHCardHeader, CHCardTitle } from '../ui/ch-card';
import { CHDropdown } from '../ui/ch-dropdown';
import { CHEmpty } from '../ui/ch-empty';

/**
 * Admin Moderation Page
 * Enterprise-grade content moderation queue with consistent design
 * Matches AdminUsers and AdminAnalytics patterns
 */

interface ModerationItem {
  id: number;
  title: string;
  type: 'Review' | 'Booking' | 'Resource';
  reason: string;
  reasonSeverity: 'low' | 'medium' | 'high' | 'critical';
  reporter: string;
  date: string;
}

export function AdminModeration() {
  const [selectedItems, setSelectedItems] = useState<number[]>([]);
  const [items, setItems] = useState<ModerationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  
  // Fetch flagged reviews from backend
  useEffect(() => {
    async function fetchFlaggedContent() {
      setLoading(true);
      setError(null);
      
      const response = await getFlaggedReviews();
      
      if (response.error) {
        const errorMessage = response.error || 'Failed to load flagged content';
        setError(errorMessage);
        toast.error('Error loading moderation queue', {
          description: errorMessage,
        });
      } else if (response.data) {
        // Transform API reviews to moderation items
        const transformedItems: ModerationItem[] = response.data.items.map((review: Review) => ({
          id: review.id,
          title: `Review for ${review.resource?.name || 'Unknown Resource'}`,
          type: 'Review' as const,
          reason: review.is_flagged ? 'Flagged Content' : 'Under Review',
          reasonSeverity: 'medium' as const,
          reporter: review.user?.full_name || review.user?.username || 'Unknown',
          date: new Date(review.created_at).toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
          }),
        }));
        setItems(transformedItems);
      }
      
      setLoading(false);
    }
    
    fetchFlaggedContent();
  }, []);
  
  // Sample moderation data (fallback)
  const fallbackItems: ModerationItem[] = [
    {
      id: 1,
      title: 'Inappropriate review comment for Wells Library Study Room',
      type: 'Review',
      reason: 'Inappropriate Language',
      reasonSeverity: 'high',
      reporter: 'Sarah Johnson',
      date: 'Nov 10, 2025',
    },
    {
      id: 2,
      title: 'Suspected fake booking for Luddy Hall Lab 2150',
      type: 'Booking',
      reason: 'Suspicious Activity',
      reasonSeverity: 'medium',
      reporter: 'System Auto-detect',
      date: 'Nov 10, 2025',
    },
    {
      id: 3,
      title: 'Spam resource listing - "Free Pizza in Room 101"',
      type: 'Resource',
      reason: 'Spam Content',
      reasonSeverity: 'critical',
      reporter: 'Michael Chen',
      date: 'Nov 9, 2025',
    },
    {
      id: 4,
      title: 'Offensive profile picture on user account',
      type: 'Review',
      reason: 'Inappropriate Content',
      reasonSeverity: 'high',
      reporter: 'Emily Rodriguez',
      date: 'Nov 9, 2025',
    },
    {
      id: 5,
      title: 'Repeated no-show bookings from same user',
      type: 'Booking',
      reason: 'Policy Violation',
      reasonSeverity: 'medium',
      reporter: 'System Auto-detect',
      date: 'Nov 8, 2025',
    },
    {
      id: 6,
      title: 'Misleading resource description for Conference Room B',
      type: 'Resource',
      reason: 'Misinformation',
      reasonSeverity: 'low',
      reporter: 'David Park',
      date: 'Nov 8, 2025',
    },
  ];
  
  // Get reason badge variant based on severity
  const getReasonBadgeVariant = (severity: ModerationItem['reasonSeverity']) => {
    if (severity === 'critical') return 'danger';
    if (severity === 'high') return 'danger';
    if (severity === 'medium') return 'warning';
    return 'neutral';
  };
  
  // Get type badge variant
  const getTypeBadgeVariant = (type: ModerationItem['type']) => {
    if (type === 'Review') return 'info';
    if (type === 'Booking') return 'warning';
    return 'neutral';
  };
  
  // Toggle item selection
  const toggleItemSelection = (id: number) => {
    if (selectedItems.includes(id)) {
      setSelectedItems(selectedItems.filter(itemId => itemId !== id));
    } else {
      setSelectedItems([...selectedItems, id]);
    }
  };
  
  // Toggle all items
  const toggleAllItems = () => {
    if (selectedItems.length === items.length) {
      setSelectedItems([]);
    } else {
      setSelectedItems(items.map(i => i.id));
    }
  };
  
  // Bulk resolve
  const handleBulkResolve = async () => {
    if (selectedItems.length === 0) return;
    
    setActionLoading(-1); // -1 indicates bulk action
    
    try {
      const promises = selectedItems.map(id => hideReview(id));
      const results = await Promise.all(promises);
      
      const failures = results.filter(r => r.error);
      
      if (failures.length === 0) {
        toast.success(`Resolved ${selectedItems.length} item(s) successfully`);
        // Remove resolved items from list
        setItems(items.filter(item => !selectedItems.includes(item.id)));
        setSelectedItems([]);
      } else {
        toast.error('Some items could not be resolved', {
          description: `${failures.length} of ${selectedItems.length} failed`,
        });
      }
    } catch (err) {
      toast.error('Failed to resolve items');
    }
    
    setActionLoading(null);
  };
  
  // Item actions
  const handleItemAction = async (action: string, itemId: number) => {
    if (action === 'resolve') {
      setActionLoading(itemId);
      
      const response = await hideReview(itemId);
      
      if (response.error) {
        toast.error('Failed to resolve item', {
          description: response.error,
        });
      } else {
        toast.success('Item resolved successfully');
        // Remove item from list
        setItems(items.filter(item => item.id !== itemId));
      }
      
      setActionLoading(null);
    } else {
      // Other actions not yet implemented
      toast.info(`${action} functionality coming soon`);
    }
  };
  
  return (
    <div className="min-h-screen bg-canvas">
      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-iu-crimson"></div>
        </div>
      )}
      
      {/* Error State */}
      {error && !loading && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 m-6">
          <p className="text-sm text-red-800">
            Failed to load moderation queue. Please try refreshing the page.
          </p>
        </div>
      )}
      
      {/* Main Content */}
      {!loading && !error && (
      <>
      {/* Admin Header - Normalized spacing */}
      <header className="bg-surface border-b border-default px-6 lg:px-8 py-8">
        <div className="max-w-[1400px] mx-auto">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div>
              <h1 className="text-h1 text-fg-default mb-2">Moderation Queue</h1>
              <p className="text-body text-fg-muted">
                Review and moderate flagged content
              </p>
            </div>
            
            <div className="flex items-center gap-3">
              <CHButton variant="secondary" size="md">
                <Filter className="w-4 h-4" />
                Filter
              </CHButton>
            </div>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="px-6 lg:px-8 py-6">
        <div className="max-w-[1400px] mx-auto flex flex-col gap-6">
          
          {/* Bulk Action Bar */}
          {selectedItems.length > 0 && (
            <div className="bg-success-light border border-success/20 rounded-lg px-5 py-4 flex items-center justify-between gap-4 animate-slide-up">
              <p className="text-caption-semibold text-fg-default">
                {selectedItems.length} item{selectedItems.length > 1 ? 's' : ''} selected
              </p>
              
              <CHButton
                variant="primary"
                size="md"
                onClick={handleBulkResolve}
                disabled={actionLoading === -1}
              >
                {actionLoading === -1 ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
                ) : (
                  <CheckCircle className="w-4 h-4" />
                )}
                Resolve Selected
              </CHButton>
            </div>
          )}
          
          {/* Moderation Table Card */}
          <CHCard elevation="sm">
            <CHCardHeader className="border-b border-border-muted">
              <CHCardTitle>Flagged Items ({items.length})</CHCardTitle>
            </CHCardHeader>
            
            <CHCardContent className="p-0">
              {items.length === 0 ? (
                <div className="p-12">
                  <CHEmpty
                    icon={<CheckCircle className="w-8 h-8 text-fg-muted" />}
                    title="No items to moderate"
                    description="All flagged content has been reviewed. Great work!"
                  />
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="bg-subtle border-b border-border-muted">
                        <th className="w-12 px-5 py-3.5">
                          <input
                            type="checkbox"
                            checked={selectedItems.length === items.length && items.length > 0}
                            onChange={toggleAllItems}
                            className="w-4 h-4 rounded border-default text-brand-crimson 
                              focus:ring-2 focus:ring-brand-crimson cursor-pointer
                              transition-colors"
                            aria-label="Select all items"
                          />
                        </th>
                        <th className="px-4 py-3.5 text-left text-caption-semibold text-fg-default">
                          Item
                        </th>
                        <th className="px-4 py-3.5 text-left text-caption-semibold text-fg-default w-32">
                          Type
                        </th>
                        <th className="px-4 py-3.5 text-left text-caption-semibold text-fg-default w-48">
                          Reason
                        </th>
                        <th className="px-4 py-3.5 text-left text-caption-semibold text-fg-default w-40">
                          Reporter
                        </th>
                        <th className="px-4 py-3.5 text-left text-caption-semibold text-fg-default w-32">
                          Date
                        </th>
                        <th className="px-4 py-3.5 text-center text-caption-semibold text-fg-default w-20">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    
                    <tbody className="divide-y divide-border-muted">
                      {items.map((item, index) => (
                        <tr
                          key={item.id}
                          className={`
                            transition-colors duration-150 cursor-pointer
                            ${selectedItems.includes(item.id) ? 'bg-[#F9F7F6]' : 'hover:bg-[#F9F7F6]'}
                          `}
                          onClick={() => toggleItemSelection(item.id)}
                        >
                          {/* Checkbox */}
                          <td className="px-5 py-4">
                            <input
                              type="checkbox"
                              checked={selectedItems.includes(item.id)}
                              onChange={() => toggleItemSelection(item.id)}
                              className="w-4 h-4 rounded border-default text-brand-crimson 
                                focus:ring-2 focus:ring-brand-crimson cursor-pointer
                                transition-colors"
                              aria-label={`Select ${item.title}`}
                            />
                          </td>
                          
                          {/* Title */}
                          <td className="px-4 py-4">
                            <p className="text-caption text-fg-default line-clamp-2">
                              {item.title}
                            </p>
                          </td>
                          
                          {/* Type Badge */}
                          <td className="px-4 py-4">
                            <CHBadge variant={getTypeBadgeVariant(item.type)} size="sm">
                              {item.type}
                            </CHBadge>
                          </td>
                          
                          {/* Reason Badge */}
                          <td className="px-4 py-4">
                            <CHBadge variant={getReasonBadgeVariant(item.reasonSeverity)} size="sm">
                              {item.reason}
                            </CHBadge>
                          </td>
                          
                          {/* Reporter */}
                          <td className="px-4 py-4">
                            <p className="text-caption text-fg-muted truncate">
                              {item.reporter}
                            </p>
                          </td>
                          
                          {/* Date */}
                          <td className="px-4 py-4">
                            <p className="text-caption text-fg-muted whitespace-nowrap">
                              {item.date}
                            </p>
                          </td>
                          
                          {/* Actions Dropdown */}
                          <td className="px-4 py-4">
                            <div className="flex items-center justify-center">
                              <CHDropdown
                                trigger={
                                  <button 
                                    className="p-2 hover:bg-subtle rounded-md transition-colors
                                      focus-visible:outline-none focus-visible:ring-2 
                                      focus-visible:ring-brand-crimson focus-visible:ring-offset-2"
                                    aria-label="Item actions"
                                    disabled={actionLoading === item.id}
                                  >
                                    {actionLoading === item.id ? (
                                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
                                    ) : (
                                      <MoreVertical className="w-4 h-4 text-fg-muted" />
                                    )}
                                  </button>
                                }
                                items={[
                                  { 
                                    label: 'View Details', 
                                    onClick: () => handleItemAction('view', item.id) 
                                  },
                                  { 
                                    label: 'Resolve', 
                                    onClick: () => handleItemAction('resolve', item.id) 
                                  },
                                  { 
                                    label: 'Escalate', 
                                    onClick: () => handleItemAction('escalate', item.id) 
                                  },
                                  { type: 'separator' },
                                  { 
                                    label: 'Dismiss', 
                                    onClick: () => handleItemAction('dismiss', item.id), 
                                    danger: true 
                                  },
                                ]}
                              />
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CHCardContent>
          </CHCard>
        </div>
      </main>
      </>
      )}
    </div>
  );
}
