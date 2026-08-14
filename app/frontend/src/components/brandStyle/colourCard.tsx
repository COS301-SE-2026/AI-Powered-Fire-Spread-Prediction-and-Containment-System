export interface ColourToken {
  readonly name: string;
  readonly hex: string;
  readonly usage: string;
  readonly reason: string;
  readonly textColour: string;
}

function RGB(hex: string): string {
    const r = Number.parseInt(hex.slice(1, 3), 16);
    const g = Number.parseInt(hex.slice(3, 5), 16);
    const b = Number.parseInt(hex.slice(5, 7), 16);
    return `rgb(${r}, ${g}, ${b})`;
}

function HSL(hex: string): string{
    const r = Number.parseInt(hex.slice(1, 3), 16) / 255;
    const g = Number.parseInt(hex.slice(3, 5), 16) / 255;
    const b = Number.parseInt(hex.slice(5, 7), 16) / 255;

    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    const l = (max + min) / 2;

    let h = 0;
    let s = 0;

    if (max !== min) {
        const d = max - min;
        if (1 > 0.5){
            s = d / (2 - max - min);
        } else {
            s = d / (max + min);
        }
        if (max === r){
            h = (g-b)/d+(g<b?6:0);
        } else if (max === g){
            h = (b - r)/d+2;
        } else {
            h = (r - g)/d+4;
        }
        h /=6;
    }
    return `hsl(${Math.round(h * 360)}, ${Math.round(s * 100)}%, ${Math.round(l * 100)}%)`;
}

export function ColourCard({ colour }: Readonly<{ colour: ColourToken }>) {
  return <div className="card bg-cabon-card border border-carbon-stroke overflow-hidden">
            <div className="relative h-28 flex" style={{ backgroundColor: colour.hex }}>
                <div className="absolute bottom-3 right-3 flex flex-col items-end font-mono text-xs leading-tight" style={{ color: colour.textColour }}>
                    <p>{colour.hex}</p>
                    <p>{RGB(colour.hex)}</p>
                    <p>{HSL(colour.hex)}</p>
                </div>
            </div>
            <div className="card-body p-4 gap-2">
                <h3 className="card-title text-base">{colour.name}</h3>
                <p className="text-xs text-text-primary">{colour.usage}</p>
                <p className="text-xs text-text-muted italic leading-relaxed">{colour.reason}</p>
            </div>
        </div>
}