import React from 'react';

interface InfoCardProps {
  readonly label: string;
  readonly value: string;
  readonly desc: string;
}

export default function InfoCard({ label, value, desc }: InfoCardProps) {
  return (
    <div
      style={{
        border: '1px solid var(--color-carbon-stroke)',
        borderRadius: 'var(--radius-md)',
        padding: '1.75rem',
        backgroundColor: 'var(--color-carbon-input)',
      }}
    >
      <p
        style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '0.9375rem',
          color: '#A0ACC0',
          fontWeight: 600,
          letterSpacing: '0.15em',
          textTransform: 'uppercase',
          marginBottom: '0.75rem',
        }}
      >
        {label}
      </p>
      <p
        style={{
          fontFamily: 'var(--font-display)',
          fontSize: '1.5rem', // Slightly larger for better visibility
          color: '#EDEAE5',
          fontWeight: 700,
          marginBottom: '0.5rem',
        }}
      >
        {value}
      </p>
      <p
        style={{
          fontFamily: 'var(--font-body)',
          fontSize: '1rem',
          color: '#A0A8B8',
          lineHeight: 1.6,
        }}
      >
        {desc}
      </p>
    </div>
  );
}
