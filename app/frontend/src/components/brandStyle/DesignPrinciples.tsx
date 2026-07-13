import React from 'react';

export default function DesignPrinciplesSection() {
  const principles = [
    {
      label: 'Core Principle',
      title: 'Consistency',
      definition: 'The application of unified interaction patterns, component libraries, and standardized terminology across all interfaces to minimize cognitive load and maximize efficiency.',
    },
    {
      label: 'Core Principle',
      title: 'Simplicity',
      definition: 'The prioritization of removal of non-essential elements, ensuring that every component directly supports tactical decision-making.',
    },
    {
      label: 'Core Principle',
      title: 'Responsiveness',
      definition: 'The capability of the interface to dynamically adapt its layout and functionality across varying display resolutions.',
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
        These principles serve as the operational foundation for Fireaway. By prioritizing high-performance reliability and clarity, we ensure that 
        every interface decision empowers responders to make life-saving decisions with speed, accuracy, and absolute confidence.
      </p>

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr', 
        gap: '16px',
        width: '100%' 
      }}>
        {principles.map((item) => (
          <div key={item.title} style={{ 
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
              {item.label}
            </p>
            <p style={{ 
              fontFamily: 'var(--font-display)', 
              fontSize: '24px', 
              color: '#EDEAE5', 
              fontWeight: 700, 
              marginBottom: '8px' 
            }}>
              {item.title}
            </p>
            <p style={{ 
              fontFamily: 'var(--font-body)', 
              fontSize: '16px', 
              color: '#A0A8B8', 
              lineHeight: 1.6 
            }}>
              {item.definition}
            </p>
          </div>
        ))}
      </div>

    </div>
  );
}