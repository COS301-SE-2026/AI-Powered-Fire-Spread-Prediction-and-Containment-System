import { useEffect, useState } from 'react';
import { Cpu, X } from 'lucide-react';
import { useDeviceCapability } from '../../hooks/useDeviceCapability';

interface GpuNotificationProps {
    autoDismissMs?: number;
}

const SEEN_KEY = "fireaway.gpuNotificationSeen";

export default function GpuNotification({ autoDismissMs = 8000 }: GpuNotificationProps) {
    // uncomment real logic
    // const { isEligible, gpuName } = useDeviceCapability();
    const [visible, setVisible] = useState(false);

    const detected = useDeviceCapability();

    // TEMP: preview only, remove when done
    const isEligible = true;
    const gpuName = "NVIDIA GeForce RTX 3060";
    // ------------------------------------------

    function dismiss() {
        setVisible(false);
        localStorage.setItem(SEEN_KEY, "true");
    }

    useEffect(() =>{
        if (!isEligible) {
            return;
        }

        // uncomment actual logic
        // if (localStorage. getItem(SEEN_KEY) === "true") {
        //     return;
        // }

        setVisible(true);
        const timer = setTimeout(() =>{
            setVisible(false);
            localStorage.setItem(SEEN_KEY, "true");
        }, autoDismissMs);
        return () => clearTimeout(timer);
    }, [isEligible, autoDismissMs]);

    if (!visible) {
        return null;
    }

    let message = "Your GPU is eligible to contribute to Fireaway simulations.";
    if (gpuName) {
        message = `${gpuName} is eligible to contribute to Fireaway simulations.`;
    }
    return (
        <div className='toast toast-start toast-top z-100'>
            <div role="status" className='alert border relative border-ignite btn btn-primary text-text-primary'>
                <div>
                    <button type='button' className='btn btn-ghost btn-xs btn-circle absolute top-1 left-1' aria-label='Dismis notification' onClick={dismiss}>
                        <X className='size-4' aria-hidden='true' />
                    </button>
                </div>
                <Cpu className='size-8' aria-hidden="true" />
                <div>
                    <p className='text-lg font-bold'>GPU qualified</p>
                    <p className='text-base font-semibold'>{message}</p>
                </div>
            </div>
        </div>
    );
}