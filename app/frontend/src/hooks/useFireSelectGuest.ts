import { useState, useCallback } from 'react';

export function useFireSelect() {
    const [fireId, setFireId] = useState<string | null>(null);

    const handleSelectFire = useCallback((ref: string) => {
        setFireId((current) => (current === ref ? null : ref));
    }, []);

    const clearSelect = useCallback(() => setFireId(null), []);
    return { fireId, handleSelectFire, clearSelect };
}