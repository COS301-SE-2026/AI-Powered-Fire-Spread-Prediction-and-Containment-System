import Accessibility from '../components/brandStyle/Accessability';
import DesignPrinciples from '../components/brandStyle/DesignPrinciples';
import StyleGuideNav from "../components/brandStyle/navStyle";
import { ColourGroup } from '../components/brandStyle/colourGroup';
import { ColourCard, ColourToken } from '../components/brandStyle/colourCard';
import { ColourPairTable, ColourPairRow } from '../components/brandStyle/colourTable';
import { TypoCard, TypoFamily } from '../components/brandStyle/typoCard';
import { TypoTable } from '../components/brandStyle/typoTable';
import { LogoGrid } from '../components/brandStyle/logoGrid';
import { IconGrid } from '../components/brandStyle/iconGrid';
import { RulesTable } from '../components/brandStyle/rulesTable';
import { ButtonComponents } from '../components/brandStyle/componentsButton';
import { Input } from '../components/brandStyle/componentsInput';
import { Checkbox } from '../components/brandStyle/componentsCheckbox';
import { Range } from '../components/brandStyle/componentsRange';
import { EnvironmentCards, ActionCards, NearbyReport, MapOverlay } from '../components/brandStyle/componentsFirefighter';
import { Toasts } from '../components/brandStyle/componentsToasts';
import { StatusBadges } from '../components/brandStyle/componentsStatus';
import { StatusCard } from '../components/brandStyle/componentReportStatus';
import { Alerts } from '../components/brandStyle/componentsAlert';
import { Table } from '../components/brandStyle/componentsTable';
import { SearchBarComponents } from '../components/brandStyle/componentSearchBar';
import { DesignTokenTable } from '../components/brandStyle/StyleTokens';

// brand colours
const primary: ColourToken = { name: "Primary - Ignite", hex: "#FF4904 ", usage: "Buttons, links, active states", reason: "We chose this saturated orange because it reminds us of the flames. We call it Ignite (the moment a flame catches). It demands attention, which is exactly the role this colour plays in the interface. The primary colour needs to feel urgent, the same reaction for a real flame.", textColour: "#ffffff" };
const secondary: ColourToken = { name: "Secondary - Glow", hex: "#FE8024", usage: "Secondary actions, deep accents", reason: "We chose this colour by staying in the same warm-orange family as Primary rather than introducing a new hue. We call it Glow (the softer light a fire casts outward). Secondary actions doesn't compete for attention.", textColour: "#ffffff"  };
const accent: ColourToken = { name: "Accent - Torch", hex: "#FCBA3E", usage: "Highlights, callouts", reason: "We chose this colour because it needed to be different enough from Primary to draw attention on its own. We call it Torch (the brightest part of a flame). It is used to guide attention the way an actual torch would.", textColour: "#ffffff"  };

// semantic colours
const info: ColourToken = { name: "Info", hex: "#378ADD", usage: "Informational messages, wind data", reason: "We chose this cool blue for informational content. Blue feels calm and doesn't feel alarming.", textColour: "#000000" };
const success: ColourToken = { name: "Success", hex: "#1D9E75", usage: "Confirmations, humidity data", reason: "We chose green as the one colour with no relationship to fire. It is universally understood as go or good or success across cultures.", textColour: "#000000"  };
const warning: ColourToken = { name: "Warning", hex: "#FFAA00", usage: "Caution, pending states", reason: "We chose this gold-yellow, visually the step where a flame is smouldering and could still go either way. Warning is less urgent than an error.", textColour: "#000000"  };
const error: ColourToken = { name: "Error", hex: "#eb2a2b", usage: "Errors, destructive actions", reason: "We chose a dedicated red to represent fire turning dangerous (past urgent into stop). Red is also the most universally understood danger colour, which menase it's a real fire risk.", textColour: "#000000" };

// surface colors
const page: ColourToken = { name: "Page - Char", hex: "#080B12", usage: "Page canvas background", reason: "We chose a near-black rather than true black so the background has a very slight warmth, simmilar to the night sky. We called it Char (what's left in the dark once the fire's glow has faded). It is in contrast with the fire colours, the way embers stand out against a dark night.", textColour: "#ffffff" };
const sidebar: ColourToken = { name: "Sidebar", hex: "#0C0F1A", usage: "Sidebar and nav surfaces", reason: "We chose a step lighter than Char so it is visually separated from content.", textColour: "#ffffff"  };
const card: ColourToken = { name: "Card", hex: "#101420", usage: "Cards and panels", reason: "We continued the same lightening pattern one step further so grouped content reads as sitting above the page, giving depth without using shadows.", textColour: "#ffffff"  };
const input: ColourToken = { name: "Input", hex: "#151A26", usage: "Input fields", reason: "We chose to make input fields lighter again than cards specifically so they're immediately recognisable as something you interact with, not just something you read.", textColour: "#ffffff"  };
const elevated: ColourToken = { name: "Elevated", hex: "#161B2A", usage: "Elevated surfaces, modals", reason: "We chose the lightest surface tone for modals and overlays since these should feel closest to the user, sitting on top.", textColour: "#ffffff"  };
const stroke: ColourToken = { name: "Stroke", hex: "#1E2436", usage: "Borders and dividers", reason: "We chose a tone just bright enough to separate sections and draw a border.", textColour: "#ffffff" };

// text colors
const textPrimary: ColourToken = { name: "Text Primary", hex: "#ffffff", usage: "Default body and heading text", reason:  "We chose pure white for maximum contrast against our Char-dark backgrounds, since readability matters most for an emergency-response tool.", textColour: "#000000"  };
const textMuted: ColourToken = { name: "Text Muted", hex: "#A0ACC0", usage: "Secondary text, labels", reason: "We chose a cool, desaturated tone, so secondary text recedes behind primary text.", textColour: "#000000" };
const textDisabled: ColourToken = { name: "Text Disabled", hex: "#7A87A2", usage: "Disabled text and controls", reason: "We chose a lower-contrast tone on purpose here, showing disabled elements shouldn't be interactive.", textColour: "#ffffff" };
const textInverse: ColourToken = { name: "Text Inverse", hex: "#1A0500", usage: "Text on light/bright fills", reason: "We chose a near-black with a warm undertone (the same Char tone as our page background) so that text placed on bright fills like Torch still feels part of the same fire-toned system.", textColour: "#ffffff" };

// typo family
const displayFont: TypoFamily = { font: "font-display", weight: "font-extrabold", name: "Barlow Condensed", sample: "Fireaway", fallback: "sans-serif", source: "Google Fonts", license: "SIL OFL 1.1" };
const bodyFont: TypoFamily = { font: "font-body", weight: "font-normal", name: "Exo 2", sample: "Colours", fallback: "sans-serif", source: "Google Fonts", license: "SIL OFL 1.1" };
const monoFont: TypoFamily = { font: "font-mono", weight: "font-normal", name: "Fira Code", sample: "20km/h", fallback: "monospace", source: "Google Fonts", license: "SIL OFL 1.1" }

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
            <img src="/images/logo-large.png" alt="Fireaway" className="mx-auto h-80 w-auto object-contain"/>
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
              <ColourGroup title="Brand Colours" columns={3}>
                <ColourCard colour={primary} />
                <ColourCard colour={secondary} />
                <ColourCard colour={accent} />
              </ColourGroup>

              <ColourGroup title="Semantic Colours" columns={4}>
                <ColourCard colour={info} />
                <ColourCard colour={success} />
                <ColourCard colour={warning} />
                <ColourCard colour={error} />
              </ColourGroup>

              <ColourGroup title="Surface Colours" columns={3}>
                <ColourCard colour={page} />
                <ColourCard colour={sidebar} />
                <ColourCard colour={card} />
                <ColourCard colour={input} />
                <ColourCard colour={elevated} />
                <ColourCard colour={stroke} />
              </ColourGroup>

              <ColourGroup title="Text Colours" columns={4}>
                <ColourCard colour={textPrimary} />
                <ColourCard colour={textMuted} />
                <ColourCard colour={textDisabled} />
                <ColourCard colour={textInverse} />
              </ColourGroup>
            </section>

            <section id="colourpairs" className="mb-10 scroll-mt-8">
              <h3 className="mb-4">Colour Contrast Pairs</h3>
              <ColourPairTable>
                <ColourPairRow pair={{ label: "Text Primary on Page", fg: textPrimary.hex, bg: page.hex, ratio: 19.6 }} />
                <ColourPairRow pair={{ label: "Text Muted on Page", fg: textMuted.hex, bg: page.hex, ratio: 8.5 }} />
                <ColourPairRow pair={{ label: "Text Disabled on Page", fg: textDisabled.hex, bg: page.hex, ratio: 5.4 }} />
                <ColourPairRow pair={{ label: "Primary on Page", fg: primary.hex, bg: page.hex, ratio: 6.3 }} />
                <ColourPairRow pair={{ label: "Secondary on Page", fg: secondary.hex, bg: page.hex, ratio: 7.8 }} />
                <ColourPairRow pair={{ label: "Accent on Page", fg: accent.hex, bg: page.hex, ratio: 11.4 }} />
                <ColourPairRow pair={{ label: "Error on Page", fg: error.hex, bg: page.hex, ratio: 4.5 }} />
                <ColourPairRow pair={{ label: "Warning on Page", fg: warning.hex, bg: page.hex, ratio: 12 }} />
                <ColourPairRow pair={{ label: "Success on Page", fg: success.hex, bg: page.hex, ratio: 7.5 }} />
                <ColourPairRow pair={{ label: "Info on Page", fg: info.hex, bg: page.hex, ratio: 9.5 }} />

                <ColourPairRow pair={{ label: "Text Primary on Primary", fg: textPrimary.hex, bg: primary.hex, ratio: 3.1  }} />
                <ColourPairRow pair={{ label: "Text Primary on Sidebar", fg: textPrimary.hex, bg: sidebar.hex, ratio: 19.1  }} />
                <ColourPairRow pair={{ label: "Text Primary on Card", fg: textPrimary.hex, bg: card.hex, ratio: 18.3  }} />
                <ColourPairRow pair={{ label: "Text Primary on Input", fg: textPrimary.hex, bg: input.hex, ratio: 17.3  }} />
                <ColourPairRow pair={{ label: "Text Primary on Elevated", fg: textPrimary.hex, bg: elevated.hex, ratio: 17.1 }} />

                <ColourPairRow pair={{ label: "Primary on Sidebar", fg: primary.hex, bg: sidebar.hex, ratio: 6.1 }} />
                <ColourPairRow pair={{ label: "Primary on Card", fg: primary.hex, bg: card.hex, ratio: 5.9 }} />
                <ColourPairRow pair={{ label: "Primary on Input", fg: primary.hex, bg: input.hex, ratio: 5.5 }} />
                <ColourPairRow pair={{ label: "Primary on Elevated", fg: primary.hex, bg: elevated.hex, ratio: 5.5 }} />

                <ColourPairRow pair={{ label: "Text Muted on Sidebar", fg: textMuted.hex, bg: sidebar.hex, ratio: 8.5 }} />
                <ColourPairRow pair={{ label: "Text Muted on Card", fg: textMuted.hex, bg: card.hex, ratio: 8 }} />
                <ColourPairRow pair={{ label: "Text Muted on Input", fg: textMuted.hex, bg: input.hex, ratio: 7.5 }} />
                <ColourPairRow pair={{ label: "Text Muted on Elevated", fg: textMuted.hex, bg: elevated.hex, ratio: 7.4 }} />

                <ColourPairRow pair={{ label: "Text Inverse on Primary", fg: textInverse.hex, bg: primary.hex, ratio: 6.3 }} />
                <ColourPairRow pair={{ label: "Text Inverse on Secondary", fg: textInverse.hex, bg: secondary.hex, ratio: 7.8 }} />
                <ColourPairRow pair={{ label: "Text Inverse on Accent", fg: textInverse.hex, bg: accent.hex, ratio: 11.4 }} />
                <ColourPairRow pair={{ label: "Text Inverse on Error", fg: textInverse.hex, bg: error.hex, ratio: 4.5 }} />
                <ColourPairRow pair={{ label: "Text Inverse on Warning", fg: textInverse.hex, bg: warning.hex, ratio: 12 }} />
                <ColourPairRow pair={{ label: "Text Inverse on Success", fg: textInverse.hex, bg: success.hex, ratio: 7.5 }} />
                <ColourPairRow pair={{ label: "Text Inverse on Info", fg: textInverse.hex, bg: info.hex, ratio: 9.5 }} />
              </ColourPairTable>
          </section>

          <section id="typography" className="mb-10 scroll-mt-8">
            <h2 className="mb-8 pb-4 border-b border-carbon-stroke">Typography</h2>

            <div className="flex flex-col gap-8">
              <div className="grid grid-cols-3 gap-4">
                <TypoCard data={displayFont}/>
                <TypoCard data={bodyFont}/>
                <TypoCard data={monoFont}/>
              </div>
              <TypoTable/>
            </div>
          </section>

          <section id="logo" className="mb-10 scroll-mt-8">
            <h2 className="mb-8 pb-4 border-b border-carbon-stroke">Logo & Iconography</h2>
            <div className="flex flex-col gap-8">
              <LogoGrid />
              <IconGrid />
              <RulesTable title="Sizing and placement rules" variant="default"
                rules={[
                  'Place on dark backgrounds (carbon-side or darker)',
                  'Only show icons when sidebar is collapsed',
                  'Full logo: minimum width 120px',
                  'Monograp logo: minimum size 40x40px',
                ]}
                />
              <RulesTable title="Clear-space rules" variant="default"
                rules={[
                  "Logo: clear space on all sides equals the height of the logo's flame (1 unit)",
                  'Logo: clear space gets recalculated whenever it is resized.',
                  'Icons: minimum 8px padding on all sides when placed inside buttons, cards, or nav items',
                  'Icons: minimum 4px gap between an icon and adjacent text or another icon',
                ]}
                />
                <RulesTable title="Icons sizing & stroke rules" variant="default"
                rules={[
                  'Default icon size: 24x24px, stroke weight 2',
                  'Small/inline icons: 14-16px, stroke weight 2',
                  'Navigation icons (sidebar): 20-24px, stroke weight 2',
                  'Never mix stroke weights within the same view',
                ]}
                />
                <RulesTable title="Don'ts" variant="default"
                rules={[
                  "Don't stretch or distort the logo's proportions",
                  "Don't recolour the logo outside approved variants",
                  "Don't apply drop shadows, glows, or other effects",
                  "Don't rotate the logo",
                ]}
                />

            </div>
          </section>

          <section id="components" className="mb-10 scroll-mt-8">
            <h2 className="mb-8 pb-4 border-b border-carbon-stroke">Components</h2>
            <ButtonComponents />
            <Input />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
              <div className="flex flex-col gap-2">
                <EnvironmentCards />
                <NearbyReport />
                <Checkbox />
                <Range />
                <StatusBadges />
                <StatusCard/>
                <SearchBarComponents/>
              </div>

              <div className="flex flex-col gap-2">
                <ActionCards />
                <MapOverlay />
                <Toasts />
                <Alerts />
              </div>
            </div>
             <Table/>
          </section>

          <section id="tokens" className="mb-10 scroll-mt-8">
            <h2 className="mb-8 pb-4 border-b border-carbon-stroke">Design Tokens</h2>
            <DesignTokenTable/>
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