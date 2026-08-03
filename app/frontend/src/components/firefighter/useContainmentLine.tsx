export function useContainmentLine(onDraw: () => void) {
    return async (wkt: string) => {
        onDraw();
        try{
            const resp = await fetch('/api/firefighter/containment-line', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({wkt})
            });
            if(!resp.ok) {
                const err = await resp.json();
                console.error("Failed to save the containment line", err.detail);
                return;
            } 
        }catch(error) {
            console.error("was unable to submit containment line", error);
        }
    };
}