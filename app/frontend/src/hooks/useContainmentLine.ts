import { useState, useCallback } from 'react';
import { useAuthHeaders } from './useAuthHeaders';
import type { CreateContainmentLine, ContainmentLines } from '../types/ContainmentLines';

export function useContainmentLine(onDraw: () => void) {
    const headers = useAuthHeaders();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const submitLine = useCallback(async (wkt: string): Promise<ContainmentLines | null> => {
        setLoading(true);
        setError(null);
        try{
            const resp = await fetch('/api/firefighter/containment-line', {
                method: 'POST',
                headers: { ...headers, 'Content-Type': 'application/json'},
                body: JSON.stringify({wkt} satisfies CreateContainmentLine)
            });
            if(!resp.ok) {
                const err = await resp.json().catch(() => null);
                const message = err?.detail ?? 'Failed to save the containment line';
                console.error("Failed to save the containment line", err.detail);
                setError(message);
                return null;
            }

            const saved: ContainmentLines = await resp.json();
            onDraw();
            return saved;
        }catch(err) {
            console.error("was unable to submit containment line", error);
            setError(err instanceof Error ? err.message : 'Unknown error');
            return null;
        }finally {
            setLoading(false);
        }
    }, [headers, onDraw]);

    return { submitLine, loading, error };
}