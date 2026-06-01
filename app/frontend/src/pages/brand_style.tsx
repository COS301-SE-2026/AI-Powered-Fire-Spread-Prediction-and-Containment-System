import Head from 'next/head';
import { useState, useEffect } from 'react';

import ColoursSection from '../components/brandStyle/ColoursSection';
import TypographySection from '../components/brandStyle/TypographySection';
import LogoSection from '../components/brandStyle/LogoSection';
import ComponentsSection from '../components/brandStyle/ComponentsSection';
import AccessibilitySection from '../components/brandStyle/AccessabilitySection';
import DesignPrinciplesSection from '../components/brandStyle/DesignPrinciplesSection';
import StyleGuideNav        from "../components/brandStyle/navStyle";

const sections = [
  { id: 'colours', label: 'Colour Palette', Component: ColoursSection },
  { id: 'typography', label: 'Typography', Component: TypographySection },
  { id: 'logo', label: 'Logo & Iconography', Component: LogoSection },
  { id: 'components', label: 'UI Components', Component: ComponentsSection },
  { id: 'accessibility', label: 'Accessibility', Component: AccessibilitySection },
  { id: 'principles', label: 'Design Principles', Component: DesignPrinciplesSection },
];

export default function StyleGuidePage() {
  const [active, setActive] = useState('colours');

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => { 
          if (e.isIntersecting) setActive(e.target.id); 
        });
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
    <div className="sg-root">
    
    {/* background */}
      <div className="global-atmos">
        <div className="ga-bloom-primary" />
        <div className="ga-bloom-secondary" />
        <div className="ga-bloom-tertiary" />
      </div>

      {/*navbar*/}
      <aside className="sg-sidebar sidebar-surface">
        <StyleGuideNav active={active} scrollTo={scrollTo} />
      </aside> 
     
      {/* main */}
      <main className="sg-main">
        <div className="sg-content">

          {/* hero */}
          <div className="sg-hero">
            <h1 style={{ fontSize: "var(--text-brand-name)" }}>
              <span className="sg-hero-brand">FIRE</span>AWAY
            </h1>
            <p className="sg-hero-label">Brand Style Guide</p><p className="sg-hero-description">
              Welcome to the Fireaway Brand Style Guide! This is where we bring our
              colors, typography, and interface elements together into a single, cohesive
              system. Because our platform is designed for emergency situations, every detail
              here focuses on making things clean and easy to navigate for responders and
              community members alike. This guide ensures that no matter who builds a piece of
              the app, Fireaway always feels familiar, trusted, and reliable.
            </p>
          </div>

          {/* sections */}
          <section id="colours" style={{ marginBottom: "96px", scrollMarginTop: "32px" }}>
            <h2 style={{ marginBottom: "16px" }}>Colour Palette</h2>
            <div style={{ height: "1px", backgroundColor: "var(--color-carbon-stroke)", marginBottom: "32px" }} />
            <ColoursSection />
          </section>

          <section id="typography" style={{ marginBottom: "96px", scrollMarginTop: "32px" }}>
            <h2 style={{ marginBottom: "16px" }}>Typography</h2>
            <div style={{ height: "1px", backgroundColor: "var(--color-carbon-stroke)", marginBottom: "32px" }} />
            <TypographySection />
          </section>

          <section id="logo" style={{ marginBottom: "96px", scrollMarginTop: "32px" }}>
            <h2 style={{ marginBottom: "16px" }}>Logo & Iconography</h2>
            <div style={{ height: "1px", backgroundColor: "var(--color-carbon-stroke)", marginBottom: "32px" }} />
            <LogoSection />
          </section>

          <section id="components" style={{ marginBottom: "96px", scrollMarginTop: "32px" }}>
            <h2 style={{ marginBottom: "16px" }}>UI Components</h2>
            <div style={{ height: "1px", backgroundColor: "var(--color-carbon-stroke)", marginBottom: "32px" }} />
            <ComponentsSection />
          </section>

          <section id="accessibility" style={{ marginBottom: "96px", scrollMarginTop: "32px" }}>
            <h2 style={{ marginBottom: "16px" }}>Accessibility</h2>
            <div style={{ height: "1px", backgroundColor: "var(--color-carbon-stroke)", marginBottom: "32px" }} />
            <AccessibilitySection />
          </section>

          <section id="principles" style={{ marginBottom: "96px", scrollMarginTop: "32px" }}>
            <h2 style={{ marginBottom: "16px" }}>Design Principles</h2>
            <div style={{ height: "1px", backgroundColor: "var(--color-carbon-stroke)", marginBottom: "32px" }} />
            <DesignPrinciplesSection />
          </section>

        </div>
      </main>

    </div>
  );
}