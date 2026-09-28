import Link from 'next/link';
import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import { Cpu, X } from 'lucide-react';
import { useDeviceCapability } from '../../hooks/useDeviceCapability';

interface GpuNotificationProps {
    autoDismissMs?: number;
}

const SEEN_KEY = "fireaway.gpuNotificationSeen";

export default function GpuNotification({ autoDismissMs = 8000 }: GpuNotificationProps) {
    // uncomment real logic
    const { isEligible } = useDeviceCapability();
    const [visible, setVisible] = useState(false);
    const router = useRouter();
    const rolePrefix = router.pathname.split('/')[1];
    const volunteerHref = `/${rolePrefix}/GpuVolunteer`

    function dismiss() {
        setVisible(false);
        localStorage.setItem(SEEN_KEY, "true");
    }

    useEffect(() =>{
        if (!isEligible) {
            return;
        }

        if (localStorage. getItem(SEEN_KEY) === "true") {
            return;
        }

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

    const message = `Your GPU looks compatible with FireAway simulations`;
    return (
        <div className='toast toast-start toast-top z-100'>
            <div 
                role="status" 
                className='alert bg-ignite  text-char border border-ignite shadow-xl flex items-start gap-3 p-4 rounded-box relative max-w-md'
            >
                <div>
                    <button type='button' className='btn btn-ghost btn-xs btn-circle absolute top-2 left-1 text-char/70 hover:text-char' aria-label='Dismiss notification' onClick={dismiss}>
                        <X className='size-4' aria-hidden='true' />
                    </button>
                </div>
                <Cpu className='size-8' aria-hidden="true" />
                <div>
                    <p className='text-lg font-bold'>Help run the simulations</p>
                    <p className='text-base font-semibold'>{message}</p>
                    <Link
                        href={volunteerHref} onClick={dismiss} className='link font-semibold mt-1 inline-blocks'                    
                    >
                        Join compute grid
                    </Link>
                </div>
            </div>
        </div>
    );
}