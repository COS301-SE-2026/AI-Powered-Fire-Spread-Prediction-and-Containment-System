type ChangelogProps = Readonly<{
    date: string;
    version: string;
    change: string;
    rationale: string;
}>;

const entries: ChangelogProps[] = [
 {
    date: 'July',
    version: '1.0',
    change: 'Initial version',
    rationale: 'Decided on the brand identity for Demo 1: wireframe-stage colour palette, typography choices, and logo rules.',
  },
  {
    date: 'August',
    version: '1.1',
    change: 'Refined brand colour palette and confirmed color contrast',
    rationale:
      'Renaming and documenting and chacking colour contrast and made the palette easier to apply consistently across the team.',
  },
  {
    date: 'August',
    version: '1.1',
    change: 'Added Design Tokens table as the single source of truth matching globals.css',
    rationale:
      'Demo 1 feedback flagged risk of the guide and codebase drifting apart. Tokens are now documented directly from the CSS variables in use.',
  },
  {
    date: 'August',
    version: '1.1',
    change: 'Expanded Components section to cover real UI states (buttons, inputs, checkboxes, range, alerts, toasts, tables, status badges/cards)',
    rationale:
      'Demo 1 only covered a handful of components in isolation. These are the components actually shipped in the working app, shown with their real variants and states.',
  },
  {
    date: 'August',
    version: '1.1',
    change: 'Added Voice & Tone section',
    rationale:
      'Not present in Demo 1. Added to give the team consistent guidance for UI copy (error messages, empty states, alerts) as more of the app copy was written.',
  },
  {
    date: 'August',
    version: '1.1',
    change: 'Added Layout & Spacing section',
    rationale:
      'Responsive behaviour was finalised during implementation, so grid and spacing rules were documented once they were locked in rather than guessed at wireframe stage.',
  },
];

function Rows() {
    const rows = [];
    for (let i = 0; i < entries.length; i++) {
        const entry = entries[i];
        rows.push (
            <tr key={`${entry.version}-${i}`} className="border-b border-carbon-stroke/50 align-top">
                <td className="py-2 pr-4 whitespace-nowrap">{entry.date}</td>
                <td className="py-2 pr-4 whitespace-nowrap">{entry.version}</td>
                <td className="py-2 pr-4 ">{entry.change}</td>
                <td className="py-2 text-text-muted">{entry.rationale}</td>
            </tr>
        );
    }
    return rows;
}

export function ChangeLog() {
    return (
        <div className="flex flex-col gap-4">
            <table className="w-full test-left border-collapse">
                <thead>
                    <tr className="border-b border-carbon-stroke">
                        <th className="py-2 pr-4 font-bold">Date</th>
                        <th className="py-2 pr-4 font-bold">Version</th>
                        <th className="py-2 pr-4 font-bold">Change</th>
                        <th className="py-2 font-bold">Rationale</th>
                    </tr>
                </thead>
                <tbody>
                    {Rows()}
                </tbody>
            </table>
        </div>
    );
}
