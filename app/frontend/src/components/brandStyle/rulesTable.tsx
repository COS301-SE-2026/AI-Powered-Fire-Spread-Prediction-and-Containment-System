interface RowProps {
  rule: string;
  variant: 'default' | 'forbidden';
}

function Row({ rule, variant }: Readonly<RowProps>) {
  const textColour = variant === 'forbidden' ? 'text-red-400' : 'text-smoke';
  return (
    <div className="flex items-start gap-3 border-b border-carbon-stroke bg-carbon-card px-4 py-3 last:border-b-0">
      <p className={`font-body text-sm leading-relaxed ${textColour}`}>{rule}</p>
    </div>
  );
}

interface TableProps {
  title: string;
  rules: string[];
  variant: 'default' | 'forbidden';
}

export function RulesTable({ title, rules, variant }: Readonly<TableProps>) {
  return (
    <div className="overflow-hidden border border-carbon-stroke">
      <div className="border-b border-carbon-stroke bg-carbon-input px-4 py-3">
        <p className="font-mono text-xs font-semibold uppercase tracking-widest text-smoke">
          {title}
        </p>
      </div>
      {rules.map((rule) => (
        <Row key={rule} variant={variant} rule={rule} />
      ))}
    </div>
  );
}
