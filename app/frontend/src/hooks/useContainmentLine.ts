import { useState, useCallback } from 'react';
import type { CreateContainmentLine, ContainmentLines } from '../types/ContainmentLines';
import { apiCall } from '../lib/api';

export function useContainmentLine(onDraw: () => void) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submitLine = useCallback(
    async (wkt: string): Promise<ContainmentLines | null> => {
      setLoading(true);
      setError(null);
      try {
        const saved: ContainmentLines = await apiCall('/api/firefighter/containment-line', 'POST', {
          wkt,
        } satisfies CreateContainmentLine);
        onDraw();
        return saved;
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : 'Unknown error';
        console.error('Failed to save the containment line', err);
        setError(message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [onDraw]
  );

  return { submitLine, loading, error };
}
