import { useEffect, useState } from "react";
import { apiCall } from "@/lib/api";

export interface SimProgress {
    stage: string | null;
    message: string | null;
}

export function useSimulationProgress(progressKey: string | null, active: boolean): SimProgress | null {
    const [progress, setProgress] = useState<SimProgress | null>(null);

    useEffect(() => {
        if (!active || !progressKey) {
            setProgress(null);
            return undefined;
        }

        let cancelled = false;
        const poll = async () => {
            try {
                const data = await apiCall(`/api/v1/workers/progress/${encodeURIComponent(progressKey)}`);
                if (!cancelled) setProgress(data);
            } catch {
                // keep the last known stage; a missed poll isn't worth surfacing
            }
        };

        poll()
        const id = setInterval(poll, 1000);
        return () => {
            cancelled = true;
            clearInterval(id);
        }
    }, [progressKey, active]);

    return progress;
}