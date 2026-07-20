interface LogoCardProps {
    src: string;
    filename: string;
    note: string;
    imgHeight: string;
    bg?: string;
}

export function LogoCard({ src, filename, note, imgHeight, bg = "bg-carbon-side" }: Readonly<LogoCardProps>) {
    return (
        <div className="overflow-hidden rounded-md border border-carbon-stroke">
            <div className={`flex h-40 items-center justify-center bg-carbon-side overflow-hidden ${bg}`}>
                <img src={src} alt={filename} className={`${imgHeight} object-contain`}/>
            </div>
            <div className="card-body border-t border-carbon-stroke p-4">
                <p className="font-mono text-sm text-flare">{filename}</p>
                <p className="font-mono text-sm text-smoke">{note}</p>
            </div>
        </div>
    );
}