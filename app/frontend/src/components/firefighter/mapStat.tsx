
export function MapStatsOverlay() {
    return(
        <div className="absolute top-16 left-4 z-10 flex flex-col gap-2">
            {/* Active fires */}
            <div className="bg-carbon-bg/80 backdrop-blur-md border border-carbon-card rounded-xl px-4 py-3 flex flex-col">
                <span className="text-[10px] font-bold tracking-widest text-neutral/40 uppercase">Active Fires</span>
                <span className="text-2xl font-display font-bold text-ignite">3</span>
                <span className="text-[10px] text-neutral/50">in your area</span>
            </div>

            {/* Nearest Fire */}
            <div className="bg-carbon-bg/80 backdrop-blur-md border border-carbon-card rounded-xl px-4 py-3 flex flex-col">
                <span className="text-[10px] font-bold tracking-widest text-neutral/40 uppercase">Nearest</span>
                <span className="text-2xl font-display font-bold text-ignite">2.7 km</span>
                <span className="text-[10px] text-neutral/50">away</span>
            </div>

            {/* Pending/Unverified */}
            <div className="bg-carbon-bg/80 backdrop-blur-md border border-carbon-card rounded-xl px-4 py-3 flex flex-col">
                <span className="text-[10px] font-bold tracking-widest text-neutral/40 uppercase">Unverified Reports</span>
                <span className="text-2xl font-display font-bold text-ignite">9</span>
                <span className="text-[10px] text-neutral/50">Unverified</span>
            </div>
        </div>
    );
}
