import React, { useState, useEffect } from 'react';
import { X, Upload, Loader2 } from 'lucide-react';
import { CHButton } from '../ui/ch-button';
import { CHInput } from '../ui/ch-input';
import { toast } from 'sonner';
import { createResource, updateResource, uploadResourceImage } from '../../api/services/resourcesService';
import type { Resource, ResourceFormData } from '../../api/types';

/**
 * ResourceFormModal
 * Modal for creating and editing resources
 * Supports image upload and all resource fields
 */

interface ResourceFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  resource?: Resource; // If provided, we're editing
}

export function ResourceFormModal({
  isOpen,
  onClose,
  onSuccess,
  resource,
}: ResourceFormModalProps) {
  const isEditing = !!resource;
  
  // Form state
  const [formData, setFormData] = useState<ResourceFormData>({
    name: '',
    type: 'room',
    description: '',
    location: '',
    capacity: undefined,
    available: true,
    amenities: [],
    hourly_rate: undefined,
    campus: '',
    building: '',
    floor: '',
    contact_email: '',
  });
  
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [amenitiesInput, setAmenitiesInput] = useState('');
  
  // Load existing resource data when edit mode
  useEffect(() => {
    if (resource) {
      setFormData({
        name: resource.name,
        type: resource.type,
        description: resource.description || '',
        location: resource.location,
        capacity: resource.capacity,
        available: resource.available,
        amenities: resource.amenities || [],
        hourly_rate: resource.hourly_rate,
        campus: resource.campus || '',
        building: resource.building || '',
        floor: resource.floor || '',
        contact_email: resource.contact_email || '',
      });
      setAmenitiesInput((resource.amenities || []).join(', '));
      if (resource.image_url) {
        setImagePreview(resource.image_url);
      }
    }
  }, [resource]);
  
  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      setFormData({
        name: '',
        type: 'room',
        description: '',
        location: '',
        capacity: undefined,
        available: true,
        amenities: [],
        hourly_rate: undefined,
        campus: '',
        building: '',
        floor: '',
        contact_email: '',
      });
      setImageFile(null);
      setImagePreview('');
      setErrors({});
      setAmenitiesInput('');
    }
  }, [isOpen]);
  
  // Handle input changes
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData({ ...formData, [name]: checked });
    } else if (type === 'number') {
      setFormData({ ...formData, [name]: value ? Number(value) : undefined });
    } else {
      setFormData({ ...formData, [name]: value });
    }
    
    // Clear error for this field
    if (errors[name]) {
      setErrors({ ...errors, [name]: '' });
    }
  };
  
  // Handle image selection
  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast.error('Please select an image file');
      return;
    }
    
    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Image must be smaller than 5MB');
      return;
    }
    
    setImageFile(file);
    
    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  };
  
  // Parse amenities from comma-separated string
  const parseAmenities = (input: string): string[] => {
    return input
      .split(',')
      .map(a => a.trim())
      .filter(a => a.length > 0);
  };
  
  // Validate form
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }
    
    if (!formData.location.trim()) {
      newErrors.location = 'Location is required';
    }
    
    if (formData.capacity && formData.capacity < 1) {
      newErrors.capacity = 'Capacity must be at least 1';
    }
    
    if (formData.hourly_rate && formData.hourly_rate < 0) {
      newErrors.hourly_rate = 'Hourly rate cannot be negative';
    }
    
    if (formData.contact_email && !formData.contact_email.includes('@')) {
      newErrors.contact_email = 'Invalid email address';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
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
      // Parse amenities
      const amenitiesList = parseAmenities(amenitiesInput);
      const submitData: ResourceFormData = {
        ...formData,
        amenities: amenitiesList.length > 0 ? amenitiesList : undefined,
      };
      
      let resourceId: number;
      
      if (isEditing && resource) {
        // Update existing resource
        const response = await updateResource(resource.id, submitData);
        
        if (response.error) {
          throw new Error(response.error);
        }
        
        resourceId = resource.id;
        toast.success('Resource updated successfully');
      } else {
        // Create new resource
        const response = await createResource(submitData);
        
        if (response.error) {
          throw new Error(response.error);
        }
        
        if (!response.data) {
          throw new Error('No data returned from server');
        }
        
        resourceId = response.data.id;
        toast.success('Resource created successfully');
      }
      
      // Upload image if provided
      if (imageFile) {
        const uploadResponse = await uploadResourceImage(resourceId, imageFile);
        
        if (uploadResponse.error) {
          toast.warning('Resource saved but image upload failed');
        } else {
          toast.success('Image uploaded successfully');
        }
      }
      
      onSuccess();
      onClose();
      
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to save resource';
      toast.error('Error saving resource', {
        description: message,
      });
    } finally {
      setIsSubmitting(false);
    }
  };
  
  if (!isOpen) return null;
  
  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-brand-black/40 z-40 animate-fade-in"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-6">
        <div
          className="bg-surface rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col animate-slide-in-up ring-1 ring-default/50"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-5 border-b border-default sticky top-0 bg-surface z-10">
            <h2 className="text-h3 text-fg-default">
              {isEditing ? 'Edit Resource' : 'Create New Resource'}
            </h2>
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
            <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
              {/* Image Upload Section */}
              <div className="rounded-xl border border-default bg-white/70 p-4 md:p-5">
                <label className="block text-caption-semibold text-fg-default mb-3">
                  Resource Image
                </label>
                
                <div className="grid gap-4 md:grid-cols-[200px_1fr] items-start">
                  {imagePreview ? (
                    <div className="relative">
                      <img
                        src={imagePreview}
                        alt="Preview"
                        className="w-full h-40 object-cover rounded-lg border border-default"
                      />
                      <button
                        type="button"
                        onClick={() => {
                          setImageFile(null);
                          setImagePreview('');
                        }}
                        className="absolute top-2 right-2 p-1.5 bg-white rounded-full shadow-lg hover:bg-subtle transition-colors"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ) : (
                    <div className="relative border-2 border-dashed border-default rounded-lg p-6 text-center bg-subtle/30 hover:bg-subtle/50 transition-colors">
                      <Upload className="w-8 h-8 text-fg-muted mx-auto mb-2" />
                      <p className="text-caption text-fg-default mb-0.5">
                        Click to upload or drag and drop
                      </p>
                      <p className="text-micro text-fg-muted">
                        PNG, JPG up to 5MB
                      </p>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleImageChange}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                      />
                    </div>
                  )}
                  
                  <div className="text-caption text-fg-muted space-y-2">
                    <p>Use high-resolution photos that showcase the resource clearly. This helps students decide faster.</p>
                    <ul className="list-disc pl-4 space-y-1">
                      <li>Recommended aspect ratio 4:3</li>
                      <li>Include amenities in the frame when possible</li>
                    </ul>
                  </div>
                </div>
              </div>
              
              <div className="grid gap-6 lg:grid-cols-2 items-start">
                {/* Basic Information Section */}
                <div className="space-y-4 rounded-xl border border-default bg-white/70 p-4 md:p-5 lg:col-span-2">
                <h3 className="text-caption-semibold text-fg-default uppercase tracking-wide text-xs">
                  Basic Information
                </h3>
              
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
                  <div className="lg:col-span-7 space-y-1">
                    <label htmlFor="name" className="block text-caption-semibold text-fg-default">
                      Resource Name *
                    </label>
                    <CHInput
                      id="name"
                      name="name"
                      placeholder="e.g., Wells Library Study Room A"
                      value={formData.name}
                      onChange={handleChange}
                      error={errors.name}
                      required
                    />
                  </div>
                  
                  <div className="lg:col-span-5 space-y-1">
                    <label htmlFor="capacity" className="block text-caption-semibold text-fg-default">
                      Capacity
                    </label>
                    <CHInput
                      id="capacity"
                      name="capacity"
                      type="number"
                      placeholder="e.g., 8"
                      value={formData.capacity?.toString() || ''}
                      onChange={handleChange}
                      error={errors.capacity}
                      min="1"
                    />
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label htmlFor="type" className="block text-caption-semibold text-fg-default">
                      Type *
                    </label>
                    <select
                      id="type"
                      name="type"
                      value={formData.type}
                      onChange={handleChange}
                      className="h-10 px-3 w-full bg-surface border border-default rounded-md text-caption text-fg-default focus:outline-none focus:ring-2 focus:ring-brand-crimson focus:border-transparent transition-all"
                      required
                    >
                      <option value="room">Room</option>
                      <option value="equipment">Equipment</option>
                      <option value="facility">Facility</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                  
                  <div className="space-y-1">
                    <label htmlFor="hourly_rate" className="block text-caption-semibold text-fg-default">
                      Hourly Rate ($)
                    </label>
                    <CHInput
                      id="hourly_rate"
                      name="hourly_rate"
                      type="number"
                      placeholder="e.g., 15.00"
                      value={formData.hourly_rate?.toString() || ''}
                      onChange={handleChange}
                      error={errors.hourly_rate}
                      min="0"
                      step="0.01"
                    />
                  </div>
                </div>
                
                <div className="space-y-1">
                  <label htmlFor="description" className="block text-caption-semibold text-fg-default">
                    Description
                  </label>
                  <textarea
                    id="description"
                    name="description"
                    placeholder="Describe the resource and its features..."
                    value={formData.description}
                    onChange={handleChange}
                    rows={2}
                    className="w-full px-3 py-2 bg-surface border border-default rounded-md text-caption text-fg-default resize-none focus:outline-none focus:ring-2 focus:ring-brand-crimson focus:border-transparent transition-all"
                  />
                </div>
              </div>
              {/* Location Details Section */}
              <div className="space-y-4 rounded-xl border border-default bg-white/70 p-4 md:p-5">
                <h3 className="text-caption-semibold text-fg-default uppercase tracking-wide text-xs">
                  Location Details
                </h3>
                
                <div className="space-y-1">
                  <label htmlFor="location" className="block text-caption-semibold text-fg-default">
                    Location *
                  </label>
                  <CHInput
                    id="location"
                    name="location"
                    placeholder="e.g., Wells Library, Floor 2, Room 204"
                    value={formData.location}
                    onChange={handleChange}
                    error={errors.location}
                    required
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-1">
                    <label htmlFor="campus" className="block text-caption-semibold text-fg-default">
                      Campus
                    </label>
                    <CHInput
                      id="campus"
                      name="campus"
                      placeholder="e.g., Bloomington"
                      value={formData.campus}
                      onChange={handleChange}
                    />
                  </div>
                  
                  <div className="space-y-1">
                    <label htmlFor="building" className="block text-caption-semibold text-fg-default">
                      Building
                    </label>
                    <CHInput
                      id="building"
                      name="building"
                      placeholder="e.g., Wells Library"
                      value={formData.building}
                      onChange={handleChange}
                    />
                  </div>
                  
                  <div className="space-y-1">
                    <label htmlFor="floor" className="block text-caption-semibold text-fg-default">
                      Floor
                    </label>
                    <CHInput
                      id="floor"
                      name="floor"
                      placeholder="e.g., 2"
                      value={formData.floor}
                      onChange={handleChange}
                    />
                  </div>
                </div>
              </div>
              {/* Additional Details Section */}
              <div className="space-y-4 rounded-xl border border-default bg-white/70 p-4 md:p-5">
                <h3 className="text-caption-semibold text-fg-default uppercase tracking-wide text-xs">
                  Additional Details
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label htmlFor="amenities" className="block text-caption-semibold text-fg-default">
                      Amenities
                    </label>
                    <input
                      id="amenities"
                      type="text"
                      placeholder="e.g., WiFi, Projector, Whiteboard"
                      value={amenitiesInput}
                      onChange={(e) => setAmenitiesInput(e.target.value)}
                      className="h-10 px-3 w-full bg-surface border border-default rounded-md text-caption text-fg-default focus:outline-none focus:ring-2 focus:ring-brand-crimson focus:border-transparent transition-all"
                    />
                    <p className="text-micro text-fg-muted italic">
                      Separate multiple amenities with commas
                    </p>
                  </div>
                  
                  <div className="space-y-1">
                    <label htmlFor="contact_email" className="block text-caption-semibold text-fg-default">
                      Contact Email
                    </label>
                    <CHInput
                      id="contact_email"
                      name="contact_email"
                      type="email"
                      placeholder="e.g., contact@example.com"
                      value={formData.contact_email}
                      onChange={handleChange}
                      error={errors.contact_email}
                    />
                  </div>
                </div>
                
                <div className="pt-1">
                  <label className="flex items-start gap-2 cursor-pointer group">
                    <input
                      type="checkbox"
                      name="available"
                      checked={formData.available}
                      onChange={handleChange}
                      className="w-4 h-4 mt-0.5 rounded border-default text-brand-crimson focus:ring-2 focus:ring-brand-crimson focus:ring-offset-1 transition-all"
                    />
                    <div>
                      <span className="text-caption text-fg-default group-hover:text-fg-default/80 transition-colors">
                        Resource is available for booking
                      </span>
                      <p className="text-micro text-fg-muted">
                        Uncheck to temporarily disable bookings
                      </p>
                    </div>
                  </label>
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
                  {isEditing ? 'Update Resource' : 'Create Resource'}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}
