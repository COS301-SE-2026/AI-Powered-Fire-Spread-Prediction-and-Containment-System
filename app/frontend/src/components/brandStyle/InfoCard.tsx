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
        padding: '28px',
        backgroundColor: 'var(--color-carbon-input)',
      }}
    >
      <p
        style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '15px',
          color: '#A0ACC0',
          fontWeight: 600,
          letterSpacing: '0.15em',
          textTransform: 'uppercase',
          marginBottom: '12px',
        }}
      >
        {label}
      </p>
      <p
        style={{
          fontFamily: 'var(--font-display)',
          fontSize: '24px', // Slightly larger for better visibility
          color: '#EDEAE5',
          fontWeight: 700,
          marginBottom: '8px',
        }}
      >
        {value}
      </p>
      <p
        style={{
          fontFamily: 'var(--font-body)',
          fontSize: '16px',
          color: '#A0A8B8',
          lineHeight: 1.6,
        }}
      >
        {desc}
      </p>
    </div>
  );
}
