import { useState, useCallback } from 'react';

export function useFireSelect() {
    const [fireLocation, setFireLocation] = useState<string | null>(null);

    const handleSelectFire = useCallback((location: string) => {
        setFireLocation((current) => (current === location ? null : location));
    }, []);

    const clearSelect = useCallback(() => setFireLocation(null), []);
    return { fireLocation, handleSelectFire, clearSelect };
}