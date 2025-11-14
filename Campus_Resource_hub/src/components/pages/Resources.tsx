import React, { useState, useEffect } from 'react';
import { Filter, Plus, Search, X, MapPin, Star, Loader2, AlertCircle } from 'lucide-react';
import { getResources } from '../../api/services/resourcesService';
import type { Resource, ResourceFilters as APIResourceFilters } from '../../api/types';
import { toast } from 'sonner';
import { CHButton } from '../ui/ch-button';
import { CHInput } from '../ui/ch-input';
import { CHBadge } from '../ui/ch-badge';
import { CHSheet } from '../ui/ch-sheet';
import { CHSwitch } from '../ui/ch-switch';
import { CHResourceCard } from '../ui/ch-resource-card';
import { CHEmpty } from '../ui/ch-empty';
import { ResourceFormModal } from '../modals/ResourceFormModal';
import { ResourceDetailModal } from '../modals/ResourceDetailModal';

/**
 * Resources Page
 * Modern image-forward browsing with filter sheet
 * Grid: 3-up desktop, 2-up tablet, 1-up mobile
 */

interface FilterState {
  categories: string[];
  location: string;
  availability: boolean;
  minRating: number;
}

export function Resources() {
  // API State
  const [resources, setResources] = useState<Resource[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // UI State
  const [searchQuery, setSearchQuery] = useState('');
  const [filterSheetOpen, setFilterSheetOpen] = useState(false);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editingResource, setEditingResource] = useState<Resource | undefined>();
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [selectedResource, setSelectedResource] = useState<Resource | null>(null);
  
  // Filter state
  const [filters, setFilters] = useState<FilterState>({
    categories: [],
    location: '',
    availability: false,
    minRating: 0,
  });
  
  // Temp filter state (used in sheet before applying)
  const [tempFilters, setTempFilters] = useState<FilterState>(filters);
  
  // Fetch resources from API
  useEffect(() => {
    fetchResources();
  }, []);
  
  const fetchResources = async (customFilters?: APIResourceFilters) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const apiFilters: APIResourceFilters = customFilters || {
        available: filters.availability || undefined,
        search: searchQuery || undefined,
      };
      
      const response = await getResources(apiFilters);
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      if (response.data) {
        setResources(response.data.items || []);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load resources';
      setError(errorMessage);
      toast.error('Error loading resources', {
        description: errorMessage,
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Category options
  const categoryOptions = [
    { id: 'library', label: 'Library' },
    { id: 'lab', label: 'Lab' },
    { id: 'study-room', label: 'Study Room' },
    { id: 'conference-room', label: 'Conference Room' },
    { id: 'equipment', label: 'Equipment' },
  ];
  
  // Location options
  const locationOptions = [
    { value: '', label: 'All Locations' },
    { value: 'wells', label: 'Wells Library' },
    { value: 'luddy', label: 'Luddy Hall' },
    { value: 'union', label: 'Student Union' },
    { value: 'imu', label: 'Indiana Memorial Union' },
    { value: 'kelley', label: 'Kelley School of Business' },
  ];
  
  // Get active filter count
  const getActiveFilterCount = () => {
    let count = 0;
    if (filters.categories.length > 0) count++;
    if (filters.location) count++;
    if (filters.availability) count++;
    if (filters.minRating > 0) count++;
    return count;
  };
  
  // Get filter chips
  const getFilterChips = () => {
    const chips: Array<{ id: string; label: string }> = [];
    
    // Category chips
    filters.categories.forEach((cat) => {
      const option = categoryOptions.find(o => o.id === cat);
      if (option) {
        chips.push({ id: `category-${cat}`, label: option.label });
      }
    });
    
    // Location chip
    if (filters.location) {
      const option = locationOptions.find(o => o.value === filters.location);
      if (option) {
        chips.push({ id: 'location', label: option.label });
      }
    }
    
    // Availability chip
    if (filters.availability) {
      chips.push({ id: 'availability', label: 'Available Only' });
    }
    
    // Rating chip
    if (filters.minRating > 0) {
      chips.push({ id: 'rating', label: `${filters.minRating}+ Stars` });
    }
    
    return chips;
  };
  
  // Remove filter chip
  const removeFilterChip = (chipId: string) => {
    if (chipId.startsWith('category-')) {
      const cat = chipId.replace('category-', '');
      setFilters({
        ...filters,
        categories: filters.categories.filter(c => c !== cat),
      });
    } else if (chipId === 'location') {
      setFilters({ ...filters, location: '' });
    } else if (chipId === 'availability') {
      setFilters({ ...filters, availability: false });
    } else if (chipId === 'rating') {
      setFilters({ ...filters, minRating: 0 });
    }
  };
  
  // Toggle category in temp filters
  const toggleCategory = (categoryId: string) => {
    if (tempFilters.categories.includes(categoryId)) {
      setTempFilters({
        ...tempFilters,
        categories: tempFilters.categories.filter(c => c !== categoryId),
      });
    } else {
      setTempFilters({
        ...tempFilters,
        categories: [...tempFilters.categories, categoryId],
      });
    }
  };
  
  // Reset filters
  const resetFilters = () => {
    const emptyFilters: FilterState = {
      categories: [],
      location: '',
      availability: false,
      minRating: 0,
    };
    setTempFilters(emptyFilters);
  };
  
  // Apply filters
  const applyFilters = () => {
    setFilters(tempFilters);
    setFilterSheetOpen(false);
  };
  
  // Open filter sheet
  const openFilterSheet = () => {
    setTempFilters(filters); // Copy current filters to temp
    setFilterSheetOpen(true);
  };
  
  // Debounce search query
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (!isLoading) {
        fetchResources();
      }
    }, 500); // 500ms debounce
    
    return () => clearTimeout(timeoutId);
  }, [searchQuery]);
  
  // Apply filters when they change (no debounce for filters)
  useEffect(() => {
    if (!isLoading) {
      fetchResources();
    }
  }, [filters]);
  
  const filterChips = getFilterChips();
  const activeFilterCount = getActiveFilterCount();
  
  // Loading state
  if (isLoading && resources.length === 0) {
    return (
      <div className="flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-h1 mb-1">Resources</h1>
            <p className="text-caption text-fg-muted">
              Browse and book campus resources including study rooms, labs, and equipment
            </p>
          </div>
        </div>
        
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin text-brand-crimson mx-auto mb-2" />
            <p className="text-caption text-fg-muted">Loading resources...</p>
          </div>
        </div>
      </div>
    );
  }
  
  // Error state
  if (error && resources.length === 0) {
    return (
      <div className="flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-h1 mb-1">Resources</h1>
            <p className="text-caption text-fg-muted">
              Browse and book campus resources including study rooms, labs, and equipment
            </p>
          </div>
        </div>
        
        <div className="flex items-center justify-center h-96">
          <div className="text-center max-w-md">
            <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <AlertCircle className="w-8 h-8 text-red-600" />
            </div>
            <h3 className="text-h3 mb-2">Failed to Load Resources</h3>
            <p className="text-caption text-fg-muted mb-4">{error}</p>
            <CHButton
              variant="primary"
              onClick={() => fetchResources()}
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
          <h1 className="text-h1 mb-1">Resources</h1>
          <p className="text-caption text-fg-muted">
            Browse and book campus resources including study rooms, labs, and equipment
          </p>
        </div>
        
        {/* Actions */}
        <div className="flex gap-2">
          <CHButton
            variant="secondary"
            size="md"
            onClick={openFilterSheet}
          >
            <Filter className="w-4 h-4" />
            Filters
            {activeFilterCount > 0 && (
              <CHBadge variant="info">
                {activeFilterCount}
              </CHBadge>
            )}
          </CHButton>
          
          <CHButton 
            variant="primary" 
            size="md"
            onClick={() => setCreateModalOpen(true)}
          >
            <Plus className="w-4 h-4" />
            Create Resource
          </CHButton>
        </div>
      </div>
      
      {/* Search Area */}
      <section className="section-spacing">
        <div className="flex flex-col gap-4">
          {/* Search Input */}
          <CHInput
            placeholder="Search resources by name, location, or category..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          
          {/* Filter Chips */}
          {filterChips.length > 0 && (
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-caption text-fg-muted">Active filters:</span>
              
              {filterChips.map((chip) => (
                <button
                  key={chip.id}
                  onClick={() => removeFilterChip(chip.id)}
                  className="
                    inline-flex items-center gap-2 px-3 py-1
                    bg-subtle border border-default rounded-md
                    text-caption text-fg-default
                    hover:bg-[#EEEDEB] transition-colors
                  "
                >
                  {chip.label}
                  <X className="w-3 h-3" />
                </button>
              ))}
              
              <button
                onClick={() => setFilters({
                  categories: [],
                  location: '',
                  availability: false,
                  minRating: 0,
                })}
                className="text-caption text-brand-crimson hover:underline"
              >
                Clear all
              </button>
            </div>
          )}
        </div>
      </section>
      
      {/* Resource Grid - 3-up desktop, 2-up tablet, 1-up mobile */}
      <section className="section-spacing">
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="bg-subtle rounded-lg overflow-hidden">
                  <div className="aspect-video bg-[#EEEDEB]" />
                  <div className="p-5 space-y-3">
                    <div className="h-6 bg-[#EEEDEB] rounded w-3/4" />
                    <div className="h-4 bg-[#EEEDEB] rounded w-1/2" />
                    <div className="flex justify-between">
                      <div className="h-4 bg-[#EEEDEB] rounded w-1/3" />
                      <div className="h-4 bg-[#EEEDEB] rounded w-1/4" />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : resources.length === 0 ? (
          <CHEmpty
            icon={<Search className="w-8 h-8 text-fg-muted" />}
            title="No resources found"
            description="Try adjusting your filters or search query to find what you're looking for."
            action={
              <CHButton
                variant="secondary"
                onClick={() => {
                  setSearchQuery('');
                  setFilters({
                    categories: [],
                    location: '',
                    availability: false,
                    minRating: 0,
                  });
                }}
              >
                Clear Filters
              </CHButton>
            }
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {resources.map((resource) => (
              <CHResourceCard
                key={resource.id}
                image={resource.image_url || 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&h=450&fit=crop'}
                category={resource.type.charAt(0).toUpperCase() + resource.type.slice(1)}
                title={resource.name}
                location={resource.location}
                rating={4.5} // TODO: Get from reviews when implemented
                ratingCount={0} // TODO: Get from reviews when implemented
                status={resource.available ? 'available' : 'unavailable'}
                onClick={() => {
                  setSelectedResource(resource);
                  setDetailModalOpen(true);
                }}
                onView={() => {
                  setSelectedResource(resource);
                  setDetailModalOpen(true);
                }}
                onEdit={() => {
                  setEditingResource(resource);
                  setCreateModalOpen(true);
                }}
                onDuplicate={() => console.log('Duplicate resource:', resource.id)}
              />
            ))}
          </div>
        )}
      </section>
      
      {/* Filter Sheet */}
      <CHSheet
        isOpen={filterSheetOpen}
        onClose={() => setFilterSheetOpen(false)}
        title="Filter Resources"
      >
        <div className="flex flex-col gap-6">
          {/* Category Section */}
          <div className="flex flex-col gap-3">
            <h4 className="text-caption-semibold text-fg-default">Category</h4>
            
            <div className="flex flex-col gap-2">
              {categoryOptions.map((option) => (
                <label
                  key={option.id}
                  className="flex items-center gap-3 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={tempFilters.categories.includes(option.id)}
                    onChange={() => toggleCategory(option.id)}
                    className="w-4 h-4 rounded border-default text-brand-crimson focus:ring-2 focus:ring-brand-crimson cursor-pointer"
                  />
                  <span className="text-caption text-fg-default">
                    {option.label}
                  </span>
                </label>
              ))}
            </div>
          </div>
          
          {/* Separator */}
          <div className="h-px bg-border-muted" />
          
          {/* Location Section */}
          <div className="flex flex-col gap-3">
            <h4 className="text-caption-semibold text-fg-default">Location</h4>
            
            <select
              value={tempFilters.location}
              onChange={(e) => setTempFilters({ ...tempFilters, location: e.target.value })}
              className="
                h-10 px-3 py-2 pr-10 w-full
                bg-surface border border-default rounded-md
                text-caption text-fg-default
                appearance-none cursor-pointer
                transition-all duration-150
                focus:outline-none focus:ring-2 focus:ring-brand-crimson focus:border-transparent
              "
            >
              {locationOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          
          {/* Separator */}
          <div className="h-px bg-border-muted" />
          
          {/* Availability Section */}
          <div className="flex flex-col gap-3">
            <h4 className="text-caption-semibold text-fg-default">Availability</h4>
            
            <CHSwitch
              label="Show only available resources"
              checked={tempFilters.availability}
              onCheckedChange={(checked) => setTempFilters({ ...tempFilters, availability: checked })}
            />
          </div>
          
          {/* Separator */}
          <div className="h-px bg-border-muted" />
          
          {/* Rating Section */}
          <div className="flex flex-col gap-3">
            <h4 className="text-caption-semibold text-fg-default">Minimum Rating</h4>
            
            <div className="flex flex-col gap-2">
              {[0, 3, 4, 4.5].map((rating) => (
                <label
                  key={rating}
                  className="flex items-center gap-3 cursor-pointer"
                >
                  <input
                    type="radio"
                    name="rating"
                    checked={tempFilters.minRating === rating}
                    onChange={() => setTempFilters({ ...tempFilters, minRating: rating })}
                    className="w-4 h-4 border-default text-brand-crimson focus:ring-2 focus:ring-brand-crimson cursor-pointer"
                  />
                  <div className="flex items-center gap-2">
                    {rating === 0 ? (
                      <span className="text-caption text-fg-default">Any rating</span>
                    ) : (
                      <>
                        <Star className="w-4 h-4 fill-warning text-warning" />
                        <span className="text-caption text-fg-default">
                          {rating}+ stars
                        </span>
                      </>
                    )}
                  </div>
                </label>
              ))}
            </div>
          </div>
          
          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t border-muted">
            <CHButton
              variant="secondary"
              className="flex-1"
              onClick={resetFilters}
            >
              Reset
            </CHButton>
            <CHButton
              variant="primary"
              className="flex-1"
              onClick={applyFilters}
            >
              Apply Filters
            </CHButton>
          </div>
        </div>
      </CHSheet>
      
      {/* Resource Form Modal */}
      <ResourceFormModal
        isOpen={createModalOpen}
        onClose={() => {
          setCreateModalOpen(false);
          setEditingResource(undefined);
        }}
        onSuccess={() => {
          fetchResources();
          setEditingResource(undefined);
        }}
        resource={editingResource}
      />
      
      {/* Resource Detail Modal */}
      <ResourceDetailModal
        isOpen={detailModalOpen}
        onClose={() => {
          setDetailModalOpen(false);
          setSelectedResource(null);
        }}
        resource={selectedResource}
        onEdit={() => {
          setDetailModalOpen(false);
          setEditingResource(selectedResource!);
          setCreateModalOpen(true);
        }}
        onDelete={() => {
          setDetailModalOpen(false);
          setSelectedResource(null);
          fetchResources();
        }}
      />
    </div>
  );
}
