import { useEffect } from "react";
import { useRouter } from "next/router";

export function useMapLink(onSelectFire: (ref: string) => void) {
    const router = useRouter();

    useEffect(() => {
        const { fire } = router.query;

        if (typeof fire === 'string'){
            onSelectFire(fire);
        }
    }, [router.query, onSelectFire]);
}

