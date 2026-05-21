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
          {/* <p style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '10px',
            color: '#5A6278',
            letterSpacing: '0.15em',
            textTransform: 'uppercase',
            padding: '0 20px 16px',
            borderBottom: '1px solid var(--color-carbon-stroke)',
            marginBottom: '16px',
          }}>
            // sections
          </p> */}

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

              {/*Stats*/}
              {/* <div style={{ display: 'flex', gap: '48px', justifyContent: 'center' }}>
                {[
                  { value: '10', label: 'Colour Tokens' },
                  { value: '3',  label: 'Font Families' },
                  { value: '6',  label: 'Spacing Steps' },
                  { value: 'AA', label: 'WCAG Target'   },
                ].map(({ value, label }) => (
                  <div key={label} style={{ textAlign: 'center' }}>
                    <div style={{
                      fontFamily: 'var(--font-display)',
                      fontSize: '32px',
                      fontWeight: 800,
                      color: 'var(--color-ignite)',
                      lineHeight: 1,
                      marginBottom: '4px',
                    }}>
                      {value}
                    </div>
                    <div style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '10px',
                      color: '#5A6278',
                      letterSpacing: '0.12em',
                      textTransform: 'uppercase',
                    }}>
                      {label}
                    </div>
                  </div>
                ))}
              </div> */}
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

                {/* Placeholder */}
                <div style={{
                  backgroundColor: 'var(--color-carbon-card)',
                  border: '1px dashed var(--color-carbon-stroke)',
                  borderRadius: 'var(--radius-md)',
                  padding: '48px',
                  textAlign: 'center',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '12px',
                  color: '#5A6278',
                }}>
                  {label} — coming in next commit
                </div>
              </section>
            ))}

          </div>
        </main>

      </div>
    </>
  );
}