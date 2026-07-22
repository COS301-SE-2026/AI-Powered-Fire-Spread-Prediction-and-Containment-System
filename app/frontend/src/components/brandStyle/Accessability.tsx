import React from 'react';

export default function AccessibilitySection() {
  const standards = [
    {
      label: 'Contrast',
      value: '4.5:1 Minimum',
      desc: 'All UI elements exceed minimum WCAG AA color contrast ratios for readability.',
    },
    {
      label: 'Navigability',
      value: 'Keyboard First',
      desc: 'Full support for focus management and skip-links for screen reader users.',
    },
    {
      label: 'Compatibility',
      value: 'WAI-ARIA 1.2',
      desc: 'Semantic HTML5 structure ensuring compatibility with modern assistive tech.',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      
      <p style={{
        fontFamily: 'var(--font-body)',
        fontSize: '18px',
        color: '#B0B8C8', 
        maxWidth: '800px', 
        lineHeight: '1.75',
        fontWeight: 300,
      }}>
        In emergency response, clarity is a matter of safety. FireAway is built to be accessible to everyone, ensuring that 
        whether a user is a responder or a community member in a crisis, our interface remains intuitive and readable.
      </p>

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr', 
        gap: '16px',
        width: '100%' 
      }}>
        {standards.map(({ label, value, desc }) => (
          <div key={label} style={{ 
            border: '1px solid var(--color-carbon-stroke)', 
            borderRadius: 'var(--radius-md)', 
            padding: '28px', 
            backgroundColor: 'var(--color-carbon-input)' 
          }}>
            <p style={{ 
              fontFamily: 'var(--font-mono)', 
              fontSize: '15px', 
              color: '#A0ACC0', 
              fontWeight: 600, 
              letterSpacing: '0.15em', 
              textTransform: 'uppercase', 
              marginBottom: '12px' 
            }}>
              {label}
            </p>
            <p style={{ 
              fontFamily: 'var(--font-display)', 
              fontSize: '24px', // Slightly larger for better visibility
              color: '#EDEAE5', 
              fontWeight: 700, 
              marginBottom: '8px' 
            }}>
              {value}
            </p>
            <p style={{ 
              fontFamily: 'var(--font-body)', 
              fontSize: '16px', 
              color: '#A0A8B8', 
              lineHeight: 1.6 
            }}>
              {desc}
            </p>
          </div>
        ))}
      </div>

    </div>
  );
}