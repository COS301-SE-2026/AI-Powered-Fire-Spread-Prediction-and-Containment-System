import { useEffect } from 'react';
import { useRouter } from 'next/router'

export function useLocationToMap(onFocus: (focus: { lat: number; lng: number; zoom: number}) => void){
    const router = useRouter();

    useEffect(() => {
        if (!router.isReady){
            return;
        }

        const { lat, lng, zoom } = router.query;
        if (typeof lat != 'string' || typeof lng !== 'string'){
            return;
        }

        const latNum = Number(lat);
        const lngNum = Number(lng);
        if (Number.isNaN(latNum) || Number.isNaN(lngNum)){
            return;
        }

        let zoomNum = 12;
        if (typeof zoom === 'string' && !Number.isNaN(Number(zoom))){
            zoomNum = Number(zoom);
        }

        onFocus({ lat: latNum, lng: lngNum, zoom: zoomNum});
    }, [router.isReady, router.query, onFocus]);
}