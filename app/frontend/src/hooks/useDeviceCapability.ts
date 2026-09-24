import { useState, useEffect } from 'react';

export interface DeviceCapability {
    isEligoble: boolean;
    gpuName: string;
    osName: string;
    isDesktop: boolean;
}

export function useDeviceCapability(): DeviceCapability {
    const [capability, setCapability] = useState<DeviceCapability>({
        isEligible: false,
        gpuName: 'Detecting GPU...',
        osName: 'Detecting OS...',
        isDesktop: false,
    });

    useEffect(() => {
        if (typeof window === 'undefined')
            return;

        const userAgent = navigator.userAgent;
        let os = 'Unknown OS';
        let isDesktop = false;

        if (/android/i.test(userAgent)) {
            os = 'Android';
        } else if (/iphone|ipad|ipod/i.test(userAgent)) {
            os = 'iOS';
        } else if (/macintosh|mac os x/i.test(userAgent)) {
            os = 'macOS';
        } else if (/windows/i.test(userAgent)) {
            os = 'Windows';
            isDesktop = true;
        } else if (/linux/i.test(userAgent)) {
            os = 'Linux';
            isDesktop = true;
        }

        let detectedGpu = 'Standard Graphics Adapter';
        let isNvidia = false;

        try {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            if (gl) {
                const debugInfo = (gl as WebGLRenderingContext).getExtension('WEBGL_debug_renderer_info');
                if (debugInfo) {
                    detectedGpu = (gl as WebGLRenderingContext).getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) || detectedGpu;
                    isNvidia = /nvidia|geforce|rtx|gtx|quadro|tesla/i.test(detectedGpu);
                }
            }
        } catch {
            // fallback
        }

        setCapability({
            isEligible: isDesktop && isNvidia,
            gpuName: detectedGpu,
            osName: os,
            isDesktop,
        });
    }, []);

    return capability;
}