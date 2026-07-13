export interface TypoScale {
  readonly label: string;
  readonly token: string;
  readonly size: string;
  readonly font: "font-display" | "font-body" | "font-mono"
  readonly weightName: string;
  readonly family: string;
  readonly weight: string;
  readonly lineHeight: string;
  readonly letterSpace: string;
  readonly sample: string;
}

const pageTitle: TypoScale = { label: "Page title", token: "--text-page-title", size: "text-page-title", font: "font-display", weightName: "font-extrabold", family: "Barlow Condensed", weight: "800", lineHeight: "1.05", letterSpace: "0.04em", sample: "Report a fire" };
const sectionHead: TypoScale = { label: "Section head", token: "--text-section-head", size: "text-section-head", font: "font-display", weightName: "font-bold", family: "Barlow Condensed", weight: "700", lineHeight: "1.1", letterSpace: "0.04em", sample: "Operational parameters" };
const cardTitle: TypoScale = { label: "Card title", token: "--text-card-title", size: "text-card-title", font: "font-body", weightName: "font-semibold", family: "Exo 2", weight: "600", lineHeight: "1.3", letterSpace: "normal", sample: "Report details" };
const body: TypoScale = { label: "Body", token: "--text-body", size: "text-body", font: "font-body", weightName: "font-normal", family: "Exo 2", weight: "400", lineHeight: "1.7", letterSpace: "normal", sample: "Click the map to drop a pin" };
const label: TypoScale = { label: "Label", token: "--text-label", size: "text-label", font: "font-body", weightName: "font-medium", family: "Exo 2", weight: "500", lineHeight: "1.4", letterSpace: "0.06em", sample: "Location description" };
const caption: TypoScale = { label: "Caption", token: "--text-caption", size: "text-caption", font: "font-mono", weightName: "font-normal", family: "Fira Code", weight: "400", lineHeight: "1.5", letterSpace: "normal", sample: "1.2 km · 8 min ago" };

function TableRow({ data }: Readonly<{ data: TypoScale }>) {
  return (
    <tr className="border-t border-carbon-stroke">
      <td className="font-mono text-xs font-semibold uppercase tracking-wide text-base-content/60">{data.label}</td>
      <td className="font-mono text-xs text-base-content/60">{data.token}</td>
      <td className= "text-base-content/60">{data.family}</td>
      <td className="text-base-content/60">{data.weight}</td>
      <td className="text-base-content/60">{data.lineHeight}</td>
      <td className="text-base-content/60">{data.letterSpace}</td>
      <td className={` ${data.font} ${data.size} ${data.weightName}`}>{data.sample}</td>
    </tr>
  );
}

export function TypoTable() {
  return (
    <div className="overflow-x-auto border border-carbon-stroke">
      <table className="table border-collapse">
        <thead>
          <tr>
            <th>Name</th>
            <th>Token</th>
            <th>Family</th>
            <th>Weight</th>
            <th>Line Height</th>
            <th>Letter Spacing</th>
            <th>Sample</th>
          </tr>
        </thead>
        <tbody>
          <TableRow data={pageTitle}/>
          <TableRow data={sectionHead}/>
          <TableRow data={cardTitle}/>
          <TableRow data={body}/>
          <TableRow data={label}/>
          <TableRow data={caption}/>
        </tbody>
      </table>
    </div>
  )
}