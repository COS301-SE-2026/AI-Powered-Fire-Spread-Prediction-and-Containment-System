import { useState, useCallback } from 'react';
import type { CreateContainmentLine, ContainmentLine } from '../types/ContainmentLines';
import { apiCall } from '../lib/api';

export function useContainmentLine(onDraw: () => void) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submitLine = useCallback(
    async (body: CreateContainmentLine): Promise<ContainmentLine> => {
      setLoading(true);
      setError(null);
      try{
        return await apiCall('/api/firefighter/containment-line', 'POST', body);
      }catch(err: unknown){
        const message = err instanceof Error ? err.message : 'unknown error';
        console.error('Failed to save containment line', err);
        setError(message);
        throw err;
      }finally{
        setLoading(false);
        onDraw?.();
      }
    },
    [onDraw]
  );

  const fetchLines = useCallback(
    async (fireRef: string): Promise<ContainmentLine[]> => {
      try{
        const resp = await apiCall(
          `/api/firefighter/containment-lines/${encodeURIComponent(fireRef)}`
        );
        return resp?.data ?? [];
      }catch (err){
        console.error('Failed to load containment lines', err);
        return [];
      }
    }, []
  )

  const deleteLine = useCallback(async (lineId: string): Promise<void> => {
    await apiCall(`/api/firefighter/containment-line/${encodeURIComponent(lineId)}`, 'DELETE')
  }, [])

  return { submitLine, fetchLines, loading, error, deleteLine};

 
}