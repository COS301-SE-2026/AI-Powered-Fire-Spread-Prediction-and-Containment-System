export interface TypoFamily {
    readonly font: "font-display" | "font-body" | "font-mono";
    readonly weight: string;
    readonly name: string;
    readonly sample: string;
}

export function TypoCard({ data }: Readonly<{ data: TypoFamily }>) {
    return (
        <div className="border border-base-300 bg-base-200 p-8 text-center">
            <p className={`${data.font} ${data.weight} text-3xl`}>{data.sample}</p>
            <p className="mt-2 font-mono text-xs uppercase tracking-wide text-base-content/60">{data.name}</p>
        </div>
    );
}