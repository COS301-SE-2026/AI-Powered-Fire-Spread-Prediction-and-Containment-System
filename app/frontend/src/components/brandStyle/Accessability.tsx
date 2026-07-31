import React from 'react';
import InfoCard from './InfoCard'

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
                      <InfoCard key={label} label={label} value={value} desc={desc} />
        ))}
      </div>

    </div>
  );
}