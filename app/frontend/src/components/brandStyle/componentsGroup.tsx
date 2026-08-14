export function ComponentsGroup({ title, children }) {
  return <div className="mb-6">
            <h3 className="mb-2 text-sm uppercase tracking-wide text-text-muted">
                {title}
            </h3>
            <div className="p-4 rounded-box border border-carbon-stroke bg-carbon-card">
                {children}
            </div>
        </div>
}

export function Labled({ caption, children }) {
  return <div className="flex flex-col items-center gap-1">
            {children}
            <span className="text-[11px] font-mono text-text-muted">{caption}</span>
        </div>
}