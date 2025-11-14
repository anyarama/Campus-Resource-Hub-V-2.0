import React, { useState, useEffect } from 'react';
import { X, Upload } from 'lucide-react';
import { CHDialog } from '../ui/ch-dialog';
import { CHButton } from '../ui/ch-button';
import { CHInput } from '../ui/ch-input';
import { CHTextarea } from '../ui/ch-textarea';
import { CHSelect } from '../ui/ch-select';
import { toast } from 'sonner';
import {
  createResource,
  updateResource,
  uploadResourceImage,
} from '../../api/services/resourcesService';
import type { Resource, ResourceFormData } from '../../api/types';

interface ResourceFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  resource?: Resource;
}

const amenityOptions = [
  'Whiteboard',
  'Projector',
  'Wi-Fi',
  'Power Outlets',
  'Computer',
  'Audio/Video',
  'Natural Light',
  'Accessibility',
  'Printer/Scanner',
];

const categoryOptions = [
  { value: 'room', label: 'Study Room' },
  { value: 'equipment', label: 'Equipment' },
  { value: 'facility', label: 'Facility' },
  { value: 'other', label: 'Other' },
];

const buildingOptions = [
  { value: 'wells', label: 'Wells Library' },
  { value: 'luddy', label: 'Luddy Hall' },
  { value: 'imu', label: 'Indiana Memorial Union' },
  { value: 'student-center', label: 'Student Center' },
  { value: 'chemistry', label: 'Chemistry Building' },
  { value: 'fine-arts', label: 'Fine Arts Building' },
  { value: 'ballantine', label: 'Ballantine Hall' },
  { value: 'other', label: 'Other' },
];

export function ResourceFormModal({
  isOpen,
  onClose,
  onSuccess,
  resource,
}: ResourceFormModalProps) {
  const isEditing = !!resource;

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
  const [imagePreview, setImagePreview] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [customAmenity, setCustomAmenity] = useState('');
  const [preferredHours, setPreferredHours] = useState({ start: '', end: '' });
  const formId = 'resource-form';

  const handleClose = () => {
    if (!isSubmitting) {
      onClose();
    }
  };

  const handleDialogChange = (open: boolean) => {
    if (!open) {
      handleClose();
    }
  };

  useEffect(() => {
    if (resource) {
      setFormData({
        name: resource.name,
        type: (resource.type as ResourceFormData['type']) || 'room',
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
      setImagePreview(resource.image_url || '');
      setCustomAmenity('');
      setPreferredHours({ start: '', end: '' });
    }
  }, [resource]);

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
      setCustomAmenity('');
      setPreferredHours({ start: '', end: '' });
    }
  }, [isOpen]);

  const updateField = <K extends keyof ResourceFormData>(
    key: K,
    value: ResourceFormData[K]
  ) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
    if (errors[key as string]) {
      setErrors((prev) => ({ ...prev, [key as string]: '' }));
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      toast.error('Please select an image file');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      toast.error('Image must be smaller than 10MB');
      return;
    }
    setImageFile(file);
    const reader = new FileReader();
    reader.onloadend = () => setImagePreview(reader.result as string);
    reader.readAsDataURL(file);
  };

  const toggleAmenity = (amenity: string) => {
    setFormData((prev) => {
      const list = prev.amenities || [];
      return list.includes(amenity)
        ? { ...prev, amenities: list.filter((item) => item !== amenity) }
        : { ...prev, amenities: [...list, amenity] };
    });
  };

  const addCustomAmenity = () => {
    const trimmed = customAmenity.trim();
    if (!trimmed) {
      toast.error('Enter an amenity name');
      return;
    }
    if (!(formData.amenities || []).includes(trimmed)) {
      updateField('amenities', [...(formData.amenities || []), trimmed]);
    }
    setCustomAmenity('');
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.name.trim()) newErrors.name = 'Name is required';
    if (!formData.location.trim()) newErrors.location = 'Location is required';
    if (formData.capacity && formData.capacity < 1)
      newErrors.capacity = 'Capacity must be positive';
    if (formData.hourly_rate && formData.hourly_rate < 0)
      newErrors.hourly_rate = 'Hourly rate cannot be negative';
    if (formData.contact_email && !formData.contact_email.includes('@'))
      newErrors.contact_email = 'Invalid email address';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) {
      toast.error('Please fix the errors in the form');
      return;
    }
    setIsSubmitting(true);
    try {
      const uniqueAmenities = Array.from(new Set(formData.amenities || []))
        .filter((item) => item.trim().length > 0);
      const payload: ResourceFormData = {
        ...formData,
        amenities: uniqueAmenities.length ? uniqueAmenities : undefined,
      };

      let resourceId: number;
      if (isEditing && resource) {
        const response = await updateResource(resource.id, payload);
        if (response.error) throw new Error(response.error);
        resourceId = resource.id;
        toast.success('Resource updated successfully');
      } else {
        const response = await createResource(payload);
        if (response.error) throw new Error(response.error);
        if (!response.data) throw new Error('No data returned from server');
        resourceId = response.data.id;
        toast.success('Resource created successfully');
      }

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
      toast.error('Error saving resource', { description: message });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <CHDialog
      open={isOpen}
      onOpenChange={handleDialogChange}
      title={isEditing ? 'Edit Resource' : 'Create New Resource'}
      description="Add a new campus resource for students and staff to book"
      maxWidth="xl"
      footer={
        <>
          <CHButton variant="secondary" onClick={handleClose} disabled={isSubmitting}>
            Cancel
          </CHButton>
          <CHButton type="submit" form={formId} loading={isSubmitting}>
            {isEditing ? 'Update Resource' : 'Create Resource'}
          </CHButton>
        </>
      }
    >
      <form id={formId} onSubmit={handleSubmit} className="space-y-2.5">
        <div className="space-y-1">
          {imagePreview ? (
            <div className="relative">
              <img
                src={imagePreview}
                alt="Resource preview"
                className="w-full h-44 object-cover rounded-lg border border-border-default"
              />
              <button
                type="button"
                className="absolute top-3 right-3 p-2 bg-surface rounded-full shadow-sm border border-border-default"
                onClick={() => {
                  setImageFile(null);
                  setImagePreview('');
                }}
                aria-label="Remove image"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <label className="border-2 border-dashed border-border-default rounded-lg p-3 text-center flex flex-col items-center gap-2 cursor-pointer hover:border-brand-crimson transition-colors">
              <Upload className="w-5 h-5 text-fg-muted" />
              <p className="text-caption text-fg-default font-medium">Upload resource image</p>
              <p className="text-caption text-fg-muted">PNG, JPG up to 10MB</p>
              <input type="file" accept="image/*" className="hidden" onChange={handleImageChange} />
            </label>
          )}
        </div>

        <CHInput
          label="Resource Name"
          placeholder="e.g., Wells Library - Main Study Hall"
          value={formData.name}
          onChange={(e) => updateField('name', e.target.value)}
          required
          error={errors.name}
        />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <CHSelect
            label="Category"
            placeholder="Select category"
            value={formData.type}
            onChange={(e) => updateField('type', e.target.value as ResourceFormData['type'])}
            options={categoryOptions}
            required
          />
          <CHSelect
            label="Building"
            placeholder="Select building"
            value={formData.building}
            onChange={(e) => updateField('building', e.target.value)}
            options={buildingOptions}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <CHInput
            label="Room / Location"
            placeholder="e.g., Floor 1, Room 101"
            value={formData.location}
            onChange={(e) => updateField('location', e.target.value)}
            required
            className="md:col-span-2"
            error={errors.location}
          />
          <CHInput
            label="Floor"
            placeholder="e.g., 2"
            value={formData.floor}
            onChange={(e) => updateField('floor', e.target.value)}
          />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <CHInput
            label="Capacity"
            type="number"
            placeholder="e.g., 8"
            value={formData.capacity !== undefined ? String(formData.capacity) : ''}
            onChange={(e) =>
              updateField('capacity', e.target.value ? Number(e.target.value) : undefined)
            }
            error={errors.capacity}
          />
          <CHSelect
            label="Availability"
            value={formData.available ? 'available' : 'unavailable'}
            onChange={(e) => updateField('available', e.target.value === 'available')}
            options={[
              { value: 'available', label: 'Available' },
              { value: 'unavailable', label: 'Temporarily Unavailable' },
            ]}
          />
        </div>

        <CHTextarea
          label="Details"
          placeholder="Describe amenities, special features, and booking guidelines..."
          rows={2}
          value={formData.description}
          onChange={(e) => updateField('description', e.target.value)}
        />

        <fieldset className="space-y-1 border-0 p-0">
          <legend className="text-caption-semibold text-fg-default">Amenities</legend>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {amenityOptions.map((amenity) => (
              <label
                key={amenity}
                className="flex items-center gap-2 p-2 border border-border-default rounded-lg cursor-pointer hover:border-brand-crimson transition-colors"
              >
                <input
                  type="checkbox"
                  checked={(formData.amenities || []).includes(amenity)}
                  onChange={() => toggleAmenity(amenity)}
                  className="w-4 h-4 rounded border-border-default text-brand-crimson focus:ring-2 focus:ring-brand-crimson"
                />
                <span className="text-caption text-fg-default">{amenity}</span>
              </label>
            ))}
          </div>
          <div className="flex flex-col md:flex-row md:items-end gap-3">
            <div className="flex-1">
              <CHInput
                label="Add custom amenity"
                placeholder="e.g., 3D Printer"
                value={customAmenity}
                onChange={(e) => setCustomAmenity(e.target.value)}
              />
            </div>
            <CHButton type="button" variant="secondary" onClick={addCustomAmenity}>
              Add
            </CHButton>
          </div>
          {(formData.amenities || []).length > 0 && (
            <div className="flex flex-wrap gap-2">
              {(formData.amenities || []).map((amenity) => (
                <span
                  key={amenity}
                  className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-brand-crimson/10 text-brand-crimson text-caption"
                >
                  {amenity}
                  <button
                    type="button"
                    onClick={() => toggleAmenity(amenity)}
                    aria-label={`Remove ${amenity}`}
                    className="p-0.5"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
          )}
        </fieldset>

        <CHInput
          label="Hourly Rate (optional)"
          type="number"
          placeholder="0.00"
          value={formData.hourly_rate !== undefined ? String(formData.hourly_rate) : ''}
          onChange={(e) => updateField('hourly_rate', e.target.value ? Number(e.target.value) : undefined)}
          helperText="Leave blank for free resources"
          error={errors.hourly_rate}
        />

        <div className="space-y-1">
          <label className="text-caption-semibold text-fg-default">Booking Hours</label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <CHInput
              label="Preferred Start Time"
              type="time"
              value={preferredHours.start}
              onChange={(e) => setPreferredHours({ ...preferredHours, start: e.target.value })}
            />
            <CHInput
              label="Preferred End Time"
              type="time"
              value={preferredHours.end}
              onChange={(e) => setPreferredHours({ ...preferredHours, end: e.target.value })}
            />
          </div>
        </div>

        <div className="bg-subtle/70 border border-border-default rounded-lg p-2 text-caption text-fg-muted">
          <strong className="text-fg-default">Reminder:</strong> Resources may require admin approval before appearing
          in search.
        </div>
      </form>
    </CHDialog>
  );
}
