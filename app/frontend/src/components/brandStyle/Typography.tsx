type CardProps = {
  family: string;
  token: string;
  weights: string;
  usage: string;
};

type ScaleProps = {
  label: string;
  size: string;
};

const font_samples: Record<string, React.ReactNode> = {
  "--font-display": (
    <p className = "font-display text -[40px] font-extrabold uppercase tracking wide leading-tight">
      FIREFIGHTER DASHBOARD
    </p>
  ),
  "--font-body": <p>Tshwane Distinct - Real-time Monitoring</p>,
  "--font-mono": ( <p className="font-mono text-[18px] text-[var(--color-flare)]">
    18 km/h - WInd NW - 38°C - 1.2 km away
  </p>
  ), 
};

const scale_samples: Record<string, React.ReactNode> = {
  "Page title": <h1 className="whitespace-nowrap">REPORT A FIRE</h1>,
  "Section head": <h2 className="whitespace-nowrap">OPERATIONAL PARAMETERS</h2>,
  "Card title": <h3 className="whitespace-nowrap">Report details</h3>,
  "Body": <p className="whitespace-nowrap">Click the map to drop a pin</p>,
  "Label": <label className="whitespace-nowrap">Location  Description</label>,
  "Data": <code className="whitespace-nowrap">1.2 km  8 min ago</code>,
}

function Card({ family, token, weights, usage }: CardProps) {
  return (
    <div className="border border-[var(--color-carbon-stroke)] rounded-md overflow-hidden">
      <div className="p-7 bg-[var(--color-cardon-card)]">
        {font_samples[token]}
      </div>
      <div className="grid grid-cols-[repeat(auto-fit,minmax(140px,1fr))] gap-4 p-4 px-5 bg-[var(--color-carbon-input)] border-t border-[var(--color-carbon-stroke)]">
        <div>
          <p className="font-mono text-[18px] text-[var(--color-text-muted)] font-semibold tracking-wide uppercase mb-1.5">Family</p>
          <p className="font-body text-[16px] text-[var(--color-text-primary)]">{family}</p>
        </div>
        <div>
          <p className="font-mono text-[18px] text-[var(--color-text-muted)] font-semibold tracking-wide uppercase mb-1.5">Weights</p>
          <p className="font-body text-[16px] text-[var(--color-text-primary)]">{weights}</p>
        </div>
        <div>
          <p className="font-mono text-[18px] text-[var(--color-text-muted)] font-semibold tracking-wide uppercase mb-1.5">Usage</p>
          <p className="font-body text-[16px] text-[var(--color-text-primary)]">{usage}</p>
        </div>
      </div>
    </div>
  );
}

function Scale({ label, size }: ScaleProps ) {
  return (
    <div className="grid grid-cols-[140px_100px_1fr] items-start gap-4 px-4 py-3.5 border-b border-[var(--color-carbon-stroke)] bg-[var(--color-carbon-card)]">
      <p className="font-mono text-[15px] text-[var(--color-text-muted)] font-semibold tracking-wide uppercase">{label}</p>
      <p className="font-mono text-[15px] text-[var(--color-text-muted)] font-semibold tracking-wide uppercase">{size}</p>
      {scale_samples[label]}
    </div>
  );
}

export default function Typography() {
  return (
    <div className="flex flex-col gap-8">

      <Card
        family="Barlow Condensed"
        token="--font-display"
        weights="700 : 800"
        usage="Page titles, section headings, buttons"
      />
      <Card
        family="Exo 2"
        token="--font-body"
        weights="400 : 500 : 600"
        usage="Body text, labels, form fields, descriptions"
      />
      <Card
        family="Fira Code"
        token="--font-mono"
        weights="400 : 500"
        usage="Sensor data, distances, timestamps, tags"
      />
      <div className="overflow-x-auto">
        <div className="border border-[var(--color-carbon-stroke)] rounded-md overflow-hidden">
          <div className="px-4 py-3 bg-[var(--color-carbon-input)] border-b border-[var(--color-carbon-stroke)]">
            <p className="font-mono text-[18px] text-[var(--color-text-muted)] tracking-[0.15em] font-semibold uppercase">
              Type Scale
            </p>
          </div>
          <Scale label="Page title" size="52px / 800" />
          <Scale label="Section head" size="32px / 700" /> 
          <Scale label="Card title" size="22px / 600" />  
          <Scale label="Body" size="18px / 400" />  
          <Scale label="Label" size="14px / 500" />  
          <Scale label="Data" size="14px / 400" />              
        </div>
      </div>

    </div>
  );
}