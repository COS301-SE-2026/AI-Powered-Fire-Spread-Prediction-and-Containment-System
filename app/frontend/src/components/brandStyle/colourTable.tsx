import { ReactNode } from 'react';

export interface ColourPair {
    readonly label: string;
    readonly fg: string;
    readonly bg: string;
    readonly ratio: number;
}

function Rating(ratio: number): string {
    if (ratio>=7){
        return "AAA";
    }else if (ratio >= 4.5) {
        return "AA";
    } else if (ratio >= 3){
        return "AA (large text only)";
    } else {
        return "Fail";
    }
}

export function ColourPairRow({ pair }: { pair: ColourPair}){
    const rating = Rating(pair.ratio);
    return(
        <tr>
            <td className="text-sm border-t border-carbon-stroke w-1/4">{pair.label}</td>
            <td className="border-t border-carbon-stroke w-1/4">
            <div className="px-3 py-1.5 text-xs inline-block" style={{ color:pair.fg, backgroundColor: pair.bg }}>Sample text</div>
            </td>
            <td className="font-mono text-xs border-t border-carbon-stroke w-1/4">{pair.ratio.toFixed(2)}:1</td>
            <td className="text-sm border-t border-carbon-stroke w-1/4">{rating}</td>
        </tr>
    );
}

export function ColourPairTable({ children }: { children: ReactNode }) {
    return (
        <div className="overflow-x-auto border border-carbon-stroke">
            <table className="table">
                <thead>
                    <tr className="text-text-muted text-xs uppercase tracking-wide">
                        <th>Pair</th>
                        <th>Preview</th>
                        <th>Ratio</th>
                        <th>Rating</th>
                    </tr>
                </thead>
                <tbody>{children}</tbody>
            </table>
        </div>
    )
}