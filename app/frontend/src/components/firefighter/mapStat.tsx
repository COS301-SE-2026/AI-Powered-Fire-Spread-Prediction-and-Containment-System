interface NearbyFire{
    readonly location_text: string;
    readonly distance: number;
    readonly time_ago: string;
    readonly status: string;
}

interface NearbyFireReports{
    readonly nearby_fires: NearbyFire[];
}

export function MapStatsOverlay({nearby_fires}: NearbyFireReports) {
    if(nearby_fires.length === 0){
        return(
            <div className="absolute top-16 left-4 z-10 flex flex-col gap-2">
            {/* Active fires */}
            <div className="bg-carbon-bg/80 backdrop-blur-md border border-carbon-card rounded-xl px-4 py-3 flex flex-col">
                <span className="text-[10px] font-bold tracking-widest text-text-primary/40 uppercase">Active Fires</span>
                <span className="text-2xl font-display font-bold text-ignite">0</span>
                <span className="text-[10px] text-text-primary/50">in your area</span>
            </div>

            {/* Nearest Fire */}
            <div className="bg-carbon-bg/80 backdrop-blur-md border border-carbon-card rounded-xl px-4 py-3 flex flex-col">
                <span className="text-[10px] font-bold tracking-widest text-text-primary/40 uppercase">Nearest</span>
                <span className="text-2xl font-display font-bold text-ignite">-</span>
                <span className="text-[10px] text-text-primary/50">away</span>
            </div>

            {/* Pending/Unverified */}
            <div className="bg-carbon-bg/80 backdrop-blur-md border border-carbon-card rounded-xl px-4 py-3 flex flex-col">
                <span className="text-[10px] font-bold tracking-widest text-text-primary/40 uppercase">Unverified Reports</span>
                <span className="text-2xl font-display font-bold text-ignite">0</span>
                <span className="text-[10px] text-text-primary/50">Unverified</span>
            </div>
            </div>
        )
    }

    const activeFires = nearby_fires.filter(fire => fire.status === 'verified').length;
    const unverifiedFires = nearby_fires.filter(fire => fire.status === 'pending' || fire.status === 'received').length;
    const nearestFire = nearby_fires[0].distance;

    return(
        <div className="absolute top-16 left-4 z-10 flex flex-col gap-2">
            {/* Active fires */}
            <div className="bg-carbon-bg/80 backdrop-blur-md border border-carbon-card rounded-xl px-4 py-3 flex flex-col">
                <span className="text-[10px] font-bold tracking-widest text-text-primary/40 uppercase">Active Fires</span>
                <span className="text-2xl font-display font-bold text-ignite">{activeFires}</span>
                <span className="text-[10px] text-text-primary/50">in your area</span>
            </div>

            {/* Nearest Fire */}
            <div className="bg-carbon-bg/80 backdrop-blur-md border border-carbon-card rounded-xl px-4 py-3 flex flex-col">
                <span className="text-[10px] font-bold tracking-widest text-text-primary/40 uppercase">Nearest</span>
                <span className="text-2xl font-display font-bold text-ignite">{nearestFire} km</span>
                <span className="text-[10px] text-text-primary/50">away</span>
            </div>

            {/* Pending/Unverified */}
            <div className="bg-carbon-bg/80 backdrop-blur-md border border-carbon-card rounded-xl px-4 py-3 flex flex-col">
                <span className="text-[10px] font-bold tracking-widest text-text-primary/40 uppercase">Unverified Reports</span>
                <span className="text-2xl font-display font-bold text-ignite">{unverifiedFires}</span>
                <span className="text-[10px] text-text-primary/50">Unverified</span>
            </div>
        </div>
    );
}
