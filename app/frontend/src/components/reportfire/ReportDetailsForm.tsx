'use client';

import React, { useEffect, useRef, useState } from 'react';
import { LocationField } from './LocationField';
import { DescriptionField } from './ReportDescriptionField';
import { PhotoField } from './ReportPhotoUpload';
import { LOCATION_PLACEHOLDER } from './locationConstants';

export type ReportFormData = {
  location: string;
  description: string;
  photo: File | null;
};

type Props = {
  location?: string;
  onSubmit?: (data: ReportFormData) => void;
  onLocationSearch?: (loc: { lat: number; lng: number; address: string }) => void;
};

export default function ReportDetailsForm({
  location = '',
  onSubmit = undefined,
  onLocationSearch = undefined,
}: Props) {
  const [editableLocation, setEditableLocation] = useState(location);
  const [description, setDescription] = useState('');
  const [photo, setPhoto] = useState<File | null>(null);
  const [errors, setErrors] = useState<{ location?: string; photo?: string }>({});

  // True only when location came from a map click or autocomplete selection
  const validLocationRef = useRef(false);

  useEffect(() => {
    if (location && location !== LOCATION_PLACEHOLDER) {
      validLocationRef.current = true;
      setEditableLocation(location);
      setErrors((prev) => ({ ...prev, location: undefined }));
    }
  }, [location]);

  function clearError(field: 'location' | 'photo') {
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  }

  function handleLocationChange(val: string) {
    setEditableLocation(val);
    validLocationRef.current = false;
    if (val.trim()) clearError('location');
  }

  function handleLocationValidSelect(loc: { lat: number; lng: number; address: string }) {
    validLocationRef.current = true;
    setEditableLocation(loc.address);
    clearError('location');
    onLocationSearch?.(loc);
  }

  function handlePhotoChange(file: File | null) {
    setPhoto(file);
    if (file) {
      clearError('photo');
    } else {
      setErrors((prev) => ({
        ...prev,
        photo: 'Invalid file type. Only image files (PNG, JPG, WEBP) are permitted.',
      }));
    }
  }

  function reset() {
    setEditableLocation(LOCATION_PLACEHOLDER);
    setDescription('');
    if (photo) {
      setPhoto(null);
    }
    setErrors({});
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const newErrors: { location?: string; photo?: string } = {};

    if (
      !validLocationRef.current ||
      !editableLocation.trim() ||
      editableLocation === LOCATION_PLACEHOLDER
    ) {
      newErrors.location = 'Please select a valid location from the map or search suggestions.';
    }

    if (!photo) {
      newErrors.photo =
        'Field evidence attachment is mandatory on desktop. Please upload a telemetry image.';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setErrors({});
    onSubmit?.({ location: editableLocation, description, photo });
    reset();
  }

  return (
    <form onSubmit={handleSubmit} className="w-full flex flex-col font-body">
      <h2 className="mb-4">Report details</h2>

      <div className="flex flex-col gap-4">
        <LocationField
          value={editableLocation}
          error={errors.location}
          onChange={handleLocationChange}
          onValidSelect={handleLocationValidSelect}
        />
        <DescriptionField value={description} onChange={setDescription} />
        <PhotoField value={photo} error={errors.photo} onChange={handlePhotoChange} />

        <div className="mt-1">
          <button
            type="submit"
            className="btn w-full h-11 bg-ignite border-none text-white font-display font-bold tracking-widest uppercase text-lg"
          >
            Submit Fire Report
          </button>
        </div>
      </div>
    </form>
  );
}
