import React from 'react';
import InfoCard from './InfoCard'

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