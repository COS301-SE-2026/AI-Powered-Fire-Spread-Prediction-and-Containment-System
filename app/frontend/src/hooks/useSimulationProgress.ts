import { useEffect, useState } from "react";
import { apiCall, ApiError } from "@/lib/api";

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
        let id: ReturnType<typeof setInterval> | undefined;
        const poll = async () => {
            try {
                const data = await apiCall(`/api/v1/workers/progress/${encodeURIComponent(progressKey)}`);
                if (!cancelled) setProgress(data);
            } catch (err) {
                if (err instanceof ApiError && err.status === 401) clearInterval(id);
            }
        };

        poll()
        id = setInterval(poll, 1000);
        return () => {
            cancelled = true;
            clearInterval(id);
        }
    }, [progressKey, active]);

    return progress;
}