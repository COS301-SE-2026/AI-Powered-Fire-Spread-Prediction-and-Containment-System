export default function TypographySection() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>

      {/* Three font families */}
      {[
        {
          token: '--font-display',
          family: 'Barlow Condensed',
          weights: '600 · 700 · 800',
          usage: 'Page titles, section headings, buttons',
          sample: 'FIREFIGHTER DASHBOARD',
          sampleStyle: {
            fontFamily: 'var(--font-display)',
            fontSize: '36px',
            fontWeight: 800,
            textTransform: 'uppercase' as const,
            letterSpacing: '0.04em',
            color: '#EDEAE5',
            lineHeight: 1,
          },
        },
        {
          token: '--font-body',
          family: 'Exo 2',
          weights: '300 · 400 · 500',
          usage: 'Body text, labels, form fields, descriptions',
          sample: 'Tshwane District · Real-time Monitoring',
          sampleStyle: {
            fontFamily: 'var(--font-body)',
            fontSize: '16px',
            fontWeight: 400,
            color: '#EDEAE5',
            lineHeight: 1.6,
          },
        },
        {
          token: '--font-mono',
          family: 'Fira Code',
          weights: '400 · 500',
          usage: 'Sensor data, distances, timestamps, tags',
          sample: '18 km/h · Wind NW · 38°C · 1.2 km away',
          sampleStyle: {
            fontFamily: 'var(--font-mono)',
            fontSize: '14px',
            fontWeight: 400,
            color: 'var(--color-flare)',
            lineHeight: 1.6,
          },
        },
      ].map(({ token, family, weights, usage, sample, sampleStyle }) => (
        <div key={token} style={{ border: '1px solid var(--color-carbon-stroke)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
          <div style={{ padding: '28px', backgroundColor: 'var(--color-carbon-card)' }}>
            <p style={sampleStyle}>{sample}</p>
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
            gap: '16px',
            padding: '16px 20px',
            backgroundColor: 'var(--color-carbon-input)',
            borderTop: '1px solid var(--color-carbon-stroke)',
          }}>
            {[
              { label: 'Family',  value: family  },
              { label: 'Token',   value: token   },
              { label: 'Weights', value: weights },
              { label: 'Usage',   value: usage   },
            ].map(({ label, value }) => (
              <div key={label}>
                <p style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#5A6278', letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: '4px' }}>{label}</p>
                <p style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: '#EDEAE5' }}>{value}</p>
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* Type scale */}
      <div style={{ border: '1px solid var(--color-carbon-stroke)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
        <div style={{ padding: '12px 16px', backgroundColor: 'var(--color-carbon-input)', borderBottom: '1px solid var(--color-carbon-stroke)' }}>
          <p style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#5A6278', letterSpacing: '0.15em', textTransform: 'uppercase' }}>
            Type Scale
          </p>
        </div>
        {[
          { label: 'Page title',   size: '48px', weight: '800', font: 'var(--font-display)', sample: 'REPORT A FIRE',              upper: true  },
          { label: 'Section head', size: '28px', weight: '700', font: 'var(--font-display)', sample: 'OPERATIONAL PARAMETERS',     upper: true  },
          { label: 'Card title',   size: '20px', weight: '700', font: 'var(--font-body)',    sample: 'Report details',             upper: false },
          { label: 'Body',         size: '16px', weight: '400', font: 'var(--font-body)',    sample: 'Click the map to drop a pin',upper: false },
          { label: 'Label',        size: '13px', weight: '500', font: 'var(--font-body)',    sample: 'Location · Description',     upper: false },
          { label: 'Data',         size: '13px', weight: '400', font: 'var(--font-mono)',    sample: '1.2 km · 8 min ago',         upper: false },
        ].map(({ label, size, weight, font, sample, upper }, i, arr) => (
          <div
            key={label}
            style={{
              display: 'grid',
              gridTemplateColumns: '110px 70px 1fr',
              alignItems: 'center',
              gap: '16px',
              padding: '12px 16px',
              backgroundColor: i % 2 === 0 ? 'var(--color-carbon-card)' : 'var(--color-carbon-input)',
              borderBottom: i < arr.length - 1 ? '1px solid var(--color-carbon-stroke)' : 'none',
            }}
          >
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#5A6278', letterSpacing: '0.1em', textTransform: 'uppercase' }}>{label}</p>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#5A6278' }}>{size} / {weight}</p>
            <p style={{
              fontFamily: font,
              fontSize: size,
              fontWeight: weight,
              textTransform: upper ? 'uppercase' : 'none',
              lineHeight: 1.1,
              color: '#EDEAE5',
            }}>
              {sample}
            </p>
          </div>
        ))}
      </div>

    </div>
  );
}