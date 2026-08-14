import React from "react";

interface TokenItem {
    readonly category: "Colour" | "Typography" | "Radius" | "Shadow";// | "Breakpoint";
    readonly token: string;
    readonly value: string;
    readonly usage: string;
}

const tokens: TokenItem[] = [
  { category: "Colour", token: "--color-primary", value: "#FF4904", usage: "Primary brand actions, active highlights, key CTAs" },
  { category: "Colour", token: "--color-secondary", value: "#FE8024", usage: "Secondary interactions, active hover states" },
  { category: "Colour", token: "--color-accent", value: "#FCBA3E", usage: "Accents, focal highlights, key badges" },
  { category: "Colour", token: "--color-carbon-bg", value: "#080B12", usage: "Page background canvas" },
  { category: "Colour", token: "--color-carbon-side", value: "#0C0F1A", usage: "Sidebar navigation, container panels" },
  { category: "Colour", token: "--color-carbon-card", value: "#101420", usage: "Card surfaces, table row backgrounds" },
  { category: "Colour", token: "--color-carbon-input", value: "#151A26", usage: "Form input background surfaces" },
  { category: "Colour", token: "--color-carbon-elevated", value: "#161B2A", usage: "Elevated surfaces, modals, popovers" },
  { category: "Colour", token: "--color-carbon-stroke", value: "#1E2436", usage: "Borders, dividers, subtle structural lines" },
  { category: "Colour", token: "--color-text-primary", value: "#EDEAE5", usage: "High-contrast primary body text, titles" },
  { category: "Colour", token: "--color-text-muted", value: "#A0ACC0", usage: "Secondary text, form labels, metadata" },
  { category: "Colour", token: "--color-text-disabled", value: "#7A87A2", usage: "Disabled actions, inactive indicators" },
  { category: "Colour", token: "--color-error", value: "#EB2A2B", usage: "Critical alerts, errors, danger indicators" },
  { category: "Colour", token: "--color-success", value: "#2BB75A", usage: "Success states, active online indicators" },

  { category: "Typography", token: "--font-display", value: "Barlow Condensed", usage: "Primary headings (H1, H2), uppercase tracking" },
  { category: "Typography", token: "--font-body", value: "Exo 2", usage: "Standard UI text, card titles (H3), body copy" },
  { category: "Typography", token: "--font-mono", value: "Fira Code", usage: "Code blocks, tabular data, tags, timestamps" },
  { category: "Typography", token: "--text-brand-name", value: "3.5rem - 6rem", usage: "Hero section brand titles" },
  { category: "Typography", token: "--text-page-title", value: "2rem - 3.25rem", usage: "Page level H1 headers" },
  { category: "Typography", token: "--text-section-head", value: "1.5rem - 2rem", usage: "Section level H2 headers" },
  { category: "Typography", token: "--text-card-title", value: "1.2rem - 1.375rem", usage: "Card headers H3" },
  { category: "Typography", token: "--text-body", value: "1rem - 1.125rem", usage: "Standard body copy" },
  { category: "Typography", token: "--text-label", value: "0.8125rem", usage: "Form labels, field captions" },
  { category: "Typography", token: "--text-caption", value: "0.75rem", usage: "Data cells, code blocks, small tags" },

  { category: "Radius", token: "--radius-sm", value: "2px", usage: "Subtle edges, inner tags, small badges" },
  { category: "Radius", token: "--radius-md", value: "4px", usage: "Default interactive components, standard inputs" },
  { category: "Radius", token: "--radius-selector", value: "0.25rem (4px)", usage: "DaisyUI form selection controls" },
  { category: "Radius", token: "--radius-box", value: "0.25rem (4px)", usage: "DaisyUI modal & container default corner radius" },
  { category: "Radius", token: "rounded-lg", value: "0.5rem (8px)", usage: "Buttons, standard controls, view action buttons" },
  { category: "Radius", token: "rounded-xl", value: "0.75rem (12px)", usage: "Table containers, map panels, major layout modules" },

  { category: "Shadow", token: "--depth", value: "0", usage: "Base flat surface elevation" },
  { category: "Shadow", token: "border-carbon-stroke", value: "1px solid #1E2436", usage: "Primary surface elevation technique (stroke-based separation)" },

  // not really used yet
//   { category: "Breakpoint", token: "sm", value: "640px", usage: "Mobile landscape / small tablets" },
//   { category: "Breakpoint", token: "md", value: "768px", usage: "Standard tablets" },
//   { category: "Breakpoint", token: "lg", value: "1024px", usage: "Laptops / small desktops" },
//   { category: "Breakpoint", token: "xl", value: "1280px", usage: "Standard desktop viewports" }
];

export function DesignTokenTable() {
  return <div className="overflow-x-auto rounded-2xl border border-carbon-stroke max-h-150">
      <table className="table table-pin-rows w-full">
        <thead>
          <tr className="[&>th]:bg-carbon-bg [&>th]:border-b [&>th]:border-primary/40">
            <th className="text-left text-xs font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">Category</th>
            <th className="text-left text-xs font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">Class</th>
            <th className="text-left text-xs font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">Value</th>
            <th className="text-left text-xs font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">Usage</th>
          </tr>
        </thead>
        <tbody>
          {tokens.length === 0 ? (
            <tr>
              <td colSpan={4} className="px-4 py-8 text-center text-sm font-bold text-error">
                No tokens found
              </td>
            </tr>
          ) : (
            tokens.map((t) => (
              <tr key={t.token} className="[&>td]:border-t [&>td]:border-carbon-card hover:bg-surface-hover even:bg-carbon-bg/80">
                <td className="px-4 py-3 text-sm text-text-primary">{t.category}</td>
                <td className="px-4 py-3 text-sm font-mono text-text-primary">{t.token}</td>
                <td className="px-4 py-3 text-sm text-text-primary">{t.value}</td>
                <td className="px-4 py-3 text-sm text-text-primary">{t.usage}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
}
