import React, { useEffect, useState } from 'react';

export function useRotate(){
    const [showHint, setShowHint] = useState(false);

    useEffect(() => {
        const portrait = window.matchMedia('(orientation: portrait)').matches;

        if (portrait){
            setShowHint(true);
        }
    }, []);

    function dismiss(){
        setShowHint(false);
    }

    return { showHint, dismiss };
}