import { useState, useEffect } from 'react';

export interface DeviceCapability {
    isEligible: boolean;
    gpuName: string;
    vram_mb: number | null;
    osName: string;
    isDesktop: boolean;
}

// vram is estimated based on detected NVIDIA model, will be null if unrecognised or generic
function estimateVramFromGpuName(gpuName: string): number | null {
    const name = gpuName.toLowerCase();

    // flagship, high-end
    if (/rtx\s*4090/i.test(name)) return 24576;
    if (/rtx\s*4080/i.test(name)) return 16384;
    if (/rtx\s*3090/i.test(name)) return 24576;
    if (/rtx\s*3080\s*ti/i.test(name)) return 12288;
    if (/rtx\s*3080/i.test(name)) return 10240;

    // mid-range
    if (/rtx\s*4070\s*ti/i.test(name)) return 12288;
    if (/rtx\s*4070/i.test(name)) return 12288;
    if (/rtx\s*3070/i.test(name)) return 8192;
    if (/rtx\s*4060\s*ti/i.test(name)) return 8192;
    if (/rtx\s*4060/i.test(name)) return 8192;
    if (/rtx\s*3060\s*ti/i.test(name)) return 8192;
    if (/rtx\s*3060/i.test(name)) return 12288;

    // budget/ older
    if (/rtx\s*2080/i.test(name)) return 8192;
    if (/rtx\s*2070/i.test(name)) return 8192;
    if (/rtx\s*2060/i.test(name)) return 6144;
    if (/rtx\s*1080/i.test(name)) return 8192;
    if (/rtx\s*1070/i.test(name)) return 8192;
    if (/rtx\s*1660/i.test(name)) return 6144;
    if (/rtx\s*1650/i.test(name)) return 4096;
    if (/rtx\s*1060/i.test(name)) return 6144;
    if (/rtx\s*1050/i.test(name)) return 2048;

    if (/nvidia|geforce|rtx/i.test(name)) {
        return 4096
    }

    return null;    
}

export function useDeviceCapability(): DeviceCapability {
    const [capability, setCapability] = useState<DeviceCapability>({
        isEligible: false,
        gpuName: 'Detecting GPU...',
        vram_mb: null,
        osName: 'Detecting OS...',
        isDesktop: false,
    });

    useEffect(() => {
        if (typeof window === 'undefined')
            return;

        const { userAgent } = navigator;
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

        const estimateVram = isNvidia ? estimateVramFromGpuName(detectedGpu) : null;

        setCapability({
            isEligible: isDesktop && isNvidia,
            gpuName: detectedGpu,
            vram_mb: estimateVram,
            osName: os,
            isDesktop,
        });
    }, []);

    return capability;
}