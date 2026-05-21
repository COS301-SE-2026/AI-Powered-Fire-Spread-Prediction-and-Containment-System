import Head from 'next/head';
import { useState, useEffect } from 'react';

const sections = [
  { id: 'colours',       label: 'Colour Palette'    },
  { id: 'typography',    label: 'Typography'         },
  { id: 'logo',          label: 'Logo & Iconography' },
  { id: 'components',    label: 'UI Components'      },
  { id: 'accessibility', label: 'Accessibility'      },
  { id: 'principles',    label: 'Design Principles'  },
];

export default function StyleGuidePage() {
  const [active, setActive] = useState('colours');

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => { if (e.isIntersecting) setActive(e.target.id); })
      },
      { rootMargin: '-20% 0px -60% 0px' }
    );
    sections.forEach(({ id }) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, []);

  const scrollTo = (id: string) =>
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });

  return (
    <>
      <Head>
        <title>Fireaway — Brand Style Guide</title>
      </Head>

      <div style={{ backgroundColor: 'var(--color-carbon-bg)', color: '#EDEAE5', minHeight: '100vh', display: 'flex' }}>

        {/* ── SIDEBAR ── */}
        <aside
          style={{
            position: 'sticky',
            top: 0,
            height: '100vh',
            width: '200px',
            flexShrink: 0,
            backgroundColor: 'var(--color-carbon-side)',
            borderRight: '1px solid var(--color-carbon-stroke)',
            padding: '32px 0',
            display: 'flex',
            flexDirection: 'column',
          }}
        >

          <nav style={{ display: 'flex', flexDirection: 'column' }}>
            {sections.map(({ id, label }) => (
              <button
                key={id}
                onClick={() => scrollTo(id)}
                style={{
                  width: '100%',
                  textAlign: 'left',
                  padding: '9px 20px',
                  fontFamily: 'var(--font-body)',
                  fontSize: '13px',
                  fontWeight: active === id ? 600 : 400,
                  color: active === id ? 'var(--color-ignite)' : '#A0A8B8',
                  backgroundColor: active === id ? 'rgba(232,69,0,0.08)' : 'transparent',
                  border: 'none',
                  borderLeft: `2px solid ${active === id ? 'var(--color-ignite)' : 'transparent'}`,
                  cursor: 'pointer',
                  transition: 'all 0.15s',
                }}
              >
                {label}
              </button>
            ))}
          </nav>
        </aside>

        {/* ── MAIN ── */}
        <main style={{ flex: 1, overflowY: 'auto', padding: '64px 64px' }}>
          <div style={{ maxWidth: '720px', margin: '0 auto' }}>

            {/* HERO */}
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
              paddingBottom: '56px',
              marginBottom: '56px',
              borderBottom: '1px solid var(--color-carbon-stroke)',
            }}>
              <h1 style={{
                fontFamily: 'var(--font-display)',
                fontSize: '96px',
                fontWeight: 800,
                letterSpacing: '0.04em',
                textTransform: 'uppercase',
                lineHeight: 1,
                marginBottom: '12px',
              }}>
                <span style={{ color: 'var(--color-ignite)' }}>FIRE</span>AWAY
              </h1>

              <p style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '11px',
                color: '#5A6278',
                letterSpacing: '0.25em',
                textTransform: 'uppercase',
                marginBottom: '28px',
              }}>
                Brand Style Guide
              </p>

              <p style={{
                fontFamily: 'var(--font-body)',
                fontSize: '16px',
                color: '#A0A8B8',
                maxWidth: '640px',
                lineHeight: '1.75',
                fontWeight: 300,
              }}>
                Welcome to the Fireaway Brand Style Guide! This is where we bring our
                colors, typography, and interface elements together into a single, cohesive
                system. Because our platform is designed for emergency situations, every detail
                here focuses on making things clean and easy to navigate for responders and
                community members alike. This guide ensures that no matter who builds a piece of
                the app, Fireaway always feels familiar, trusted, and reliable.
              </p>

            </div> 

            {/* SECTIONS */}
            {sections.map(({ id, label }) => (
              <section
                key={id}
                id={id}
                style={{ marginBottom: '96px', scrollMarginTop: '32px' }}
              >
                <h2 style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: '28px',
                  fontWeight: 800,
                  letterSpacing: '0.04em',
                  textTransform: 'uppercase',
                  lineHeight: 1,
                  marginBottom: '16px',
                }}>
                  {label}
                </h2>

                <div style={{
                  height: '1px',
                  backgroundColor: 'var(--color-carbon-stroke)',
                  marginBottom: '32px',
                }} />

                {/* ── COLOUR PALETTE ── */}
                {id === 'colours' && (
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
                        { name: 'Muted',     hex: '#A0A8B8', role: 'Text - secondary & labels' },
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
                            border: ['#080B12','#0C0F1A','#101420'].includes(hex)
                              ? '1px solid rgba(255,255,255,0.14)'  
                              : 'none',
                          }} />
                          <div style={{
                            padding: '12px',
                            backgroundColor: 'var(--color-carbon-card)',
                            flex: 1,                
                          }}>
                            <p style={{ fontFamily: 'var(--font-display)', fontSize: '13px', fontWeight: 700, textTransform: 'uppercase', color: '#EDEAE5', marginBottom: '4px' }}>{name}</p>
                            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: '#EDEAE5', marginBottom: '6px' }}>{hex}</p>
                            <p style={{ fontSize: '11px', color: '#A0A8B8', lineHeight: 1.5 }}>{role}</p>
                          </div>
                        </div>
                      ))}
                    </div>

                    <div style={{ border: '1px solid var(--color-carbon-stroke)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
                      {/*contrasth ratios */}
                      <div style={{ padding: '12px 16px', backgroundColor: 'var(--color-carbon-input)', borderBottom: '1px solid var(--color-carbon-stroke)' }}>
                        <p style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#5A6278', letterSpacing: '0.15em', textTransform: 'uppercase' }}>
                          Contrast Ratios — WCAG AA
                        </p>
                      </div>

                      {/* Rows */}
                      {[
                        { fg: '#EDEAE5', bg: '#080B12', pair: '#EDEAE5 on #080B12', ratio: '16.4:1', pass: true  },
                        { fg: '#A0A8B8', bg: '#080B12', pair: '#A0A8B8 on #080B12', ratio: '7.2:1',  pass: true  },
                        { fg: '#E84500', bg: '#080B12', pair: '#E84500 on #080B12', ratio: '5.1:1',  pass: true  },
                        { fg: '#FFAA00', bg: '#101420', pair: '#FFAA00 on #101420', ratio: '8.3:1',  pass: true  },
                        { fg: '#1D9E75', bg: '#101420', pair: '#1D9E75 on #101420', ratio: '4.6:1',  pass: true  },
                        { fg: '#FFFFFF', bg: '#E84500', pair: '#FFFFFF on #E84500', ratio: '3.9:1',  pass: false },
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
                          {/* Colour preview */}
                          <div style={{ display: 'flex', gap: '4px' }}>
                            <div style={{ width: '16px', height: '16px', borderRadius: '2px', backgroundColor: fg, border: '1px solid rgba(255,255,255,0.08)' }} />
                            <div style={{ width: '16px', height: '16px', borderRadius: '2px', backgroundColor: bg, border: '1px solid rgba(255,255,255,0.08)' }} />
                          </div>

                          {/* Pair label */}
                          <p style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: '#A0A8B8' }}>{pair}</p>

                          {/* Ratio */}
                          <p style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: '#EDEAE5' }}>{ratio}</p>

                          {/* Pass / Fail */}
                          <p style={{
                            fontFamily: 'var(--font-mono)',
                            fontSize: '11px',
                            color: pass ? '#1D9E75' : '#FFAA00',
                            minWidth: '80px',
                            textAlign: 'right',
                          }}>
                            {pass ? '✓ Pass' : '△ Large only'}
                          </p>
                        </div>
                      ))}
                    </div>

                  </div>
                )}

                {/* ── PLACEHOLDERS for remaining sections ── */}
                {id !== 'colours' && (
                  <div style={{ backgroundColor: 'var(--color-carbon-card)', border: '1px dashed var(--color-carbon-stroke)', borderRadius: 'var(--radius-md)', padding: '48px', textAlign: 'center', fontFamily: 'var(--font-mono)', fontSize: '12px', color: '#5A6278' }}>
                    {label} — coming in next commit
                  </div>
                )}

              </section>
            ))}

          </div>
        </main>

      </div>
    </>
  );
}