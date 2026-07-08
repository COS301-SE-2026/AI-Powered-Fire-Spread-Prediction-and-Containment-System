import { ColourToken } from '../../types/brandStyle';

export function ColourCard({ colour }: { colour: ColourToken }) {
    return(
        <div className="card bg-cabon-card border border-carbon-stroke">
            <div className="h-20 rounder-t-box" style={{ backgroundColor: colour.hex }} />
            <div className="card-body p-3 gap-1">
                <h3 className="card-title text-sm">{colour.name}</h3>
                <p className="text-xs text-text-muted">{colour.usage}</p>
                <p className="text-xs text-text-muted italic">{colour.reason}</p>
                <p className="font-mono text-xs text-flare">{colour.hex.toUpperCase()}</p>
            </div>
        </div>
    );
}