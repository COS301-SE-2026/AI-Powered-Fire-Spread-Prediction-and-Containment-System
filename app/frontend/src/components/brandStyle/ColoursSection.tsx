export default function ColoursSection() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '40px' }}>

      {/* Swatches */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: '12px' }}>
        {[
          { name: 'Ignite',    hex: '#E84500', role: 'Primary - buttons, links, active states' },
          { name: 'Torch',     hex: '#FFAA00', role: 'Accent - warnings, pending states' },
          { name: 'Contained', hex: '#1D9E75', role: 'Accent - success, contained states' },
          { name: 'Base',      hex: '#080B12', role: 'Background - page canvas' },
          { name: 'Sidebar',   hex: '#0C0F1A', role: 'Background - sidebar & nav' },
          { name: 'Card',      hex: '#101420', role: 'Background - cards & panels' },
          { name: 'Text',      hex: '#EDEAE5', role: 'Text - headings & body' },
          { name: 'Muted',     hex: '#A0ACC0', role: 'Text - secondary & labels' },
        ].map(({ name, hex, role }) => (
          <div key={hex} style={{
            border: '1px solid var(--color-carbon-stroke)',
            borderRadius: 'var(--radius-md)',
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
          }}>
            <div style={{
              height: '64px',
              flexShrink: 0,
              backgroundColor: hex,
              border: ['#080B12', '#0C0F1A', '#101420'].includes(hex)
                ? '1px solid rgba(255,255,255,0.14)'
                : 'none',
            }} />
            <div style={{
              padding: '12px',
              backgroundColor: 'var(--color-carbon-card)',
              flex: 1,
            }}>
              <p style={{ fontFamily: 'var(--font-display)', fontSize: '18px', fontWeight: 700, textTransform: 'uppercase', color: '#EDEAE5', marginBottom: '4px' }}>{name}</p>
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: '16px', color: '#EDEAE5', marginBottom: '6px' }}>{hex}</p>
              <p style={{ fontFamily: 'var(--font-body)', fontSize: '16px', color: '#A0ACC0', lineHeight: 1.5 }}>{role}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Contrast Ratios */}
      <div style={{ border: '1px solid var(--color-carbon-stroke)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
        <div style={{ padding: '12px 16px', backgroundColor: 'var(--color-carbon-input)', borderBottom: '1px solid var(--color-carbon-stroke)' }}>
          <p style={{ fontFamily: 'var(--font-mono)', fontSize: '16px', color: '#A0ACC0', fontWeight: 600, letterSpacing: '0.15em', textTransform: 'uppercase' }}>
            Contrast Ratios - WCAG AA
          </p>
        </div>

        {[
          { fg: '#EDEAE5', bg: '#080B12', pair: '#EDEAE5 on #080B12', ratio: '16.4:1', pass: true  },
          { fg: '#A0ACC0', bg: '#080B12', pair: '#A0ACC0 on #080B12', ratio: '8.58:1',  pass: true  },
          { fg: '#E84500', bg: '#080B12', pair: '#E84500 on #080B12', ratio: '6:1',  pass: true  },
          { fg: '#FFAA00', bg: '#101420', pair: '#FFAA00 on #101420', ratio: '9.62:1',  pass: true  },
          { fg: '#1D9E75', bg: '#101420', pair: '#1D9E75 on #101420', ratio: '5.42:1',  pass: true  },
          { fg: '#FFFFFF', bg: '#E84500', pair: '#FFFFFF on #E84500', ratio: '3.97:1',  pass: false },
        ].map(({ fg, bg, pair, ratio, pass }, i, arr) => (
          <div
            key={pair}
            style={{
              display: 'grid',
              gridTemplateColumns: '40px 1fr auto auto',
              alignItems: 'center',
              gap: '16px',
              padding: '12px 16px',
              backgroundColor: i % 2 === 0 ? 'var(--color-carbon-card)' : 'var(--color-carbon-input)',
              borderBottom: i < arr.length - 1 ? '1px solid var(--color-carbon-stroke)' : 'none',
            }}
          >
            <div style={{ display: 'flex', gap: '4px' }}>
              <div style={{ width: '16px', height: '16px', borderRadius: '2px', backgroundColor: fg, border: '1px solid rgba(255,255,255,0.08)' }} />
              <div style={{ width: '16px', height: '16px', borderRadius: '2px', backgroundColor: bg, border: '1px solid rgba(255,255,255,0.08)' }} />
            </div>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '16px', color: '#A0ACC0', fontWeight: 500 }}>{pair}</p>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '16px', color: '#EDEAE5', fontWeight: 500 }}>{ratio}</p>
            <p style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '15px',
              color: pass ? '#1D9E75' : '#FFAA00',
              minWidth: '80px',
              textAlign: 'right',
            }}>
              {pass ? ' Pass' : ' Large only'}
            </p>
          </div>
        ))}
      </div>

    </div>
  );
}