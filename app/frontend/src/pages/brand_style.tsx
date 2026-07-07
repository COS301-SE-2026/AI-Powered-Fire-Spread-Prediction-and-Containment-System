import Colours from '../components/brandStyle/Colours';
import Typography from '../components/brandStyle/Typography';
import Logo from '../components/brandStyle/Logos';
import Components from '../components/brandStyle/Components';
import Accessibility from '../components/brandStyle/Accessability';
import DesignPrinciples from '../components/brandStyle/DesignPrinciples';
import StyleGuideNav from "../components/brandStyle/navStyle";

export default function StyleGuidePage() {
  return (
    <div className="min-h-screen bg-base-100 flex">
    
    {/* background */}
      <div className="global-atmos">
        <div className="ga-bloom-primary" />
        <div className="ga-bloom-secondary" />
        <div className="ga-bloom-tertiary" />
      </div>

      <StyleGuideNav />
      <main className="flex-1 flex justify-center">
        <div className="w-full max-w-4xl px-6 pt-12 pb-16">

          <div className="mb-10 text-center">
            <h1 style={{ fontSize: "var(--text-brand-name)" }}>
              <span className="text-primary">FIRE</span>AWAY
            </h1>
            <p className="text-text-muted uppercase tracking-wide mt-2">Brand Style Guide</p>
            <p className="mt-4 max-w-2xl mx-auto">
              Welcome to the Fireaway Brand Style Guide! This is where we bring our
              colors, typography, and interface elements together into a single, cohesive
              system. Because our platform is designed for emergency situations, every detail
              here focuses on making things clean and easy to navigate for responders and
              community members alike. This guide ensures that no matter who builds a piece of
              the app, Fireaway always feels familiar, trusted, and reliable.
            </p>
          </div>

          <section id="colours" className="mb-10 scroll-mt-8">
            <h2 className="mb-8 pb-4 border-b border-carbon-stroke">Colours</h2>
            <Colours />
          </section>

          <section id="typography" className="mb-10 scroll-mt-8">
            <h2 className="mb-8 pb-4 border-b border-carbon-stroke">Typography</h2>
            <Typography />
          </section>

          <section id="logo" className="mb-10 scroll-mt-8">
            <h2 className="mb-8 pb-4 border-b border-carbon-stroke">Logo & Iconography</h2>
            <Logo />
          </section>

          <section id="components" className="mb-10 scroll-mt-8">
            <h2 className="mb-8 pb-4 border-b border-carbon-stroke">Comoponents</h2>
            <Components />
          </section>

          <section id="accessibility" className="mb-10 scroll-mt-8">
            <h2 className="mb-8 pb-4 border-b border-carbon-stroke">Accessibility</h2>
            <Accessibility />
          </section>

          <section id="principles" className="mb-10 scroll-mt-8">
            <h2 className="mb-8 pb-4 border-b border-carbon-stroke">Design Principles</h2>
            <DesignPrinciples />
          </section>

        </div>
      </main>

    </div>
  );
}