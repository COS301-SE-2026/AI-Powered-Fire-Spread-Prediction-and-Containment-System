import React from 'react';

interface LighthouseRow {
  readonly page: string;
  readonly accessibility: number;
  readonly bestPractices: number;
  readonly seo: number;
}

interface ContrastPair {
  readonly label: string;
  readonly ratio: string;
  readonly level: string;
}

interface InteractionRule {
  readonly label: string;
  readonly detail: string;
}

const contrastPairs: ContrastPair[] = [
  { label: "Standard text / UI components", ratio: "4.5 : 1", level: "AA" },
  { label: "Large text (14pt bold+)", ratio: "3.0 : 1", level: "AA" },
  { label: "High-urgency & form inputs", ratio: "7.0 : 1", level: "AAA" },
  { label: "Large high-urgency", ratio: "4.5 : 1", level: "AAA" },
];

const auditData: LighthouseRow[] = [
  { page: "Index Page", accessibility: 80, bestPractices: 100, seo: 82 },
  { page: "Register", accessibility: 77, bestPractices: 100, seo: 82 },
  { page: "Login", accessibility: 77, bestPractices: 100, seo: 82 },
  { page: "Landing pages", accessibility: 74, bestPractices: 96, seo: 82 },
  { page: "Report a fire", accessibility: 71, bestPractices: 96, seo: 82 },
  { page: "Admin dashboard", accessibility: 70, bestPractices: 100, seo: 82 },
  { page: "Admin analytics", accessibility: 71, bestPractices: 100, seo: 82 },
  { page: "Role approvals", accessibility: 81, bestPractices: 96, seo: 82 },
  { page: "Reportes fires", accessibility: 71, bestPractices: 100, seo: 82 },
  { page: "View", accessibility: 70, bestPractices: 100, seo: 82 },
  { page: "Firefighter dashboard", accessibility: 96, bestPractices: 100, seo: 82 },
  { page: "Fire simulation", accessibility: 96, bestPractices: 100, seo: 82 },
];

const interactionRules: InteractionRule[] = [
  { label: "Keyboard navigation", detail: "Activation via Enter / Space. Escape closes overlays. Zero focus traps." },
  { label: "Focus indicator", detail: "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 (visible against all dark surfaces)." },
  { label: "Motion reduction", detail: "prefers-reduced-motion: reduce collapses transitions to 0.01ms." },
];

function LighthouseTableRow({ data }: Readonly<{ data: LighthouseRow }>) {
  return (
    <tr className="border-t border-carbon-stroke">
      <td className="text-base-content/80">{data.page}</td>
      <td className="font-mono text-text-primary">{data.accessibility}</td>
      <td className="font-mono text-text-primary">{data.bestPractices}</td>
      <td className="font-mono text-text-primary">{data.seo}</td>
    </tr>
  );
}

function ContrastTableRow({ data }: Readonly<{ data: ContrastPair }>) {
  return (
    <tr className="border-t border-carbon-stroke">
      <td className="text-text-primary">{data.label}</td>
      <td className="font-mono text-text-primary">{data.ratio}</td>
      <td className="font-mono text-xs font-semibold uppercase tracking-wide text-text-primary">{data.level}</td>
    </tr>
  );
}

function RuleTableRow({ data }: Readonly<{ data: InteractionRule }>) {
  return (
    <tr className="border-t border-carbon-stroke">
      <td className="text-text-primary text-xs font-semibold uppercase tracking-wide whitespace-nowrap align-top py-3">{data.label}</td>
      <td className="text-text-primary align-top py-3">{data.detail}</td>
    </tr>
  );
}

export default function AccessibilitySection() {
  return (
    <div className="flex flex-col gap-8">

      <div className="flex flex-col gap-2">
        <p className="text-text-primary">
          FireAway targets WCAG 2.2 Level AA conformance as a baseline, so emergency interfaces remain fully operable for all responders and community members.
        </p>
      </div>

      <div className="flex flex-col gap-3">
        <h3 className="mb-0.5 text-sm uppercase tracking-wide text-text-muted">
          Colour Contrast
        </h3>
        <div className="overflow-x-auto border border-carbon-stroke">
          <table className="table border-collapse">
            <thead>
              <tr>
                <th>Context</th>
                <th>Minimum Ratio</th>
                <th>Level</th>
              </tr>
            </thead>
            <tbody>
              {contrastPairs.map((row) => (
                <ContrastTableRow key={row.label} data={row} />
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <a href="#colourpairs" className="btn btn-ghost text-text-primary">↑ Go to Colour Pair Table</a>

      <div className="flex flex-col gap-3">
        <h3 className="mb-0.5 text-sm uppercase tracking-wide text-text-muted">
          Automated Lighthouse Audit
        </h3>
        <div className="overflow-x-auto border border-carbon-stroke">
          <table className="table border-collapse">
            <thead>
              <tr>
                <th>Page</th>
                <th>Accessibility</th>
                <th>Best Practices</th>
                <th>SEO</th>
              </tr>
            </thead>
            <tbody>
              {auditData.map((row) => (
                <LighthouseTableRow key={row.page} data={row} />
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        <h3 className="mb-0.5 text-sm uppercase tracking-wide text-text-muted">
          Interaction & Assistive Support - Target Behaviour
        </h3>
        <p className="text-base-content/60 text-sm">
          These are the accessibility rules the app is being built against - not yet fully implemented across all pages.
        </p>
        <div className="overflow-x-auto border border-carbon-stroke">
          <table className="table border-collapse">
            <tbody>
              {interactionRules.map((row) => (
                <RuleTableRow key={row.label} data={row} />
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}