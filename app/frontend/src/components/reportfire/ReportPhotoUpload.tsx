'use client';

import React, { useEffect, useState, useRef } from 'react';
import { Paperclip, Check } from 'lucide-react';
import { Alert } from '../shared/Alerts';

interface PhotoProps {
  readonly value: File | null;
  readonly error?: string;
  readonly onChange: (file: File | null) => void;
}

export function PhotoField({ value, error = '', onChange }: PhotoProps) {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!value) {
      setPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(value);
    setPreviewUrl(url);

    return () => URL.revokeObjectURL(url);
  }, [value]);

  function handlePhotoChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0] ?? null;

    if (!file) return;

    if (!file.type.startsWith('image/')) {
      onChange(null);
      e.target.value = '';
      return;
    }
    onChange(file);
  }
  return (
    <div className="w-full">
      <span className="label-text font-semibold text-white mb-2 block">Attach Evidence</span>
      <input
        ref={fileRef}
        type="file"
        accept="image/*"
        onChange={handlePhotoChange}
        className="hidden"
      />
      <button
        type="button"
        onClick={() => fileRef.current?.click()}
        className="h-11 w-full flex items-center justify-center gap-2 rounded-md border text-sm transition-colors duration-150"
      >
        {value ? (
          <>
            <Check size={14} strokeWidth={2.5} className="text-status-success" />
            <span className="truncate max-w-60 font-mono text-xs text-white/80">{value.name}</span>
          </>
        ) : (
          <>
            <Paperclip size={14} />
            <span>Attach Image</span>
          </>
        )}
      </button>

      {previewUrl && (
        <div className="mt-3  mx-auto w-fit rounded-md border border-carbon-stroke overflow-hidden bg-surface-input shadow-md">
          <img
            src={previewUrl}
            alt="Evidence preview"
            className="max-h-48 max-w-full object-contain block"
          />
        </div>
      )}
      {error && <Alert variant="error" message={error} />}
    </div>
  );
}
