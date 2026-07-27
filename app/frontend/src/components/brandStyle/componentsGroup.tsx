export function ComponentsGroup({ title, children }) {
    return (
        <div className="mb-10">
            <h3 className="mb-4 text-sm uppercase tracking-wide text-text-muted">
                {title}
            </h3>
            <div className="flex flex-wrap items-center gap-6 p-6 rounded-box border border-carbon-stroke bg-carbon-card">
                {children}
            </div>
        </div>
    );
}

export function Labled({ caption, children }) {
    return (
        <div className="flex flex-col items-center gap-2">
            {children}
            <span className="text-[11px] font-mono text-text-muted">{caption}</span>
        </div>
    );
}