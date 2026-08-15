export interface TypoFamily {
  readonly font: 'font-display' | 'font-body' | 'font-mono';
  readonly weight: string;
  readonly name: string;
  readonly sample: string;
  readonly fallback: string;
  readonly source: string;
  readonly license: string;
}

export function TypoCard({ data }: Readonly<{ data: TypoFamily }>) {
  return (
    <div className="border border-carbon-stroke bg-base-200 p-8 text-center">
      <p className={`${data.font} ${data.weight} text-3xl`}>{data.sample}</p>
      <p className="mt-2 font-mono text-xs uppercase tracking-wide text-base-content/60">
        {data.name}
      </p>
      <p className="mt-4 font-mono text-xs ">Fallback: {data.fallback}</p>
      <p className="mt-1 font-mono text-xs uppercase tracking-wide text-base-content/60">
        {data.source} | {data.license}
      </p>
    </div>
  );
}
