import React from 'react';

interface ToggleProps {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  className?: string; 
}

export default function Toggle({ label, checked, onChange, className = 'toggle-primary' }: ToggleProps) {
  return (
    <div className="form-control w-full">
      <label className="label cursor-pointer justify-between gap-4 py-2">
        <span className="label-text font-semibold text-sm tracking-wide">{label}</span>
        <input
          type="checkbox"
          className={`toggle toggle-sm ${className}`}
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
        />
      </label>
    </div>
  );
}