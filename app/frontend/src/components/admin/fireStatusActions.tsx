import React, { useState, useEffect } from 'react';
import { useFireStatus } from '@/hooks/useFireStatus';
import type { FireReportDetailResponse, FireStatus, ReportStatus } from '@/types/Report';
import { Card } from './Card';

interface FireStatusActionProps {
    readonly reportRef: string;
    readonly status: ReportStatus;
    readonly fireStatus: FireStatus;
    readonly onStatusChange: (report: FireReportDetailResponse) => void;
}

export function FireStatusActions({ reportRef, status, fireStatus, onStatusChange }: FireStatusActionProps) {
    const { updateFireStatus, loading, error } = useFireStatus();
    const [success, setSuccess] = useState<string | null>(null);

    useEffect(() => {
        if (!success) return;
        const timer = setTimeout(() => setSuccess(null), 3000);
        return () => clearTimeout(timer);
    }, [success]);

    const handleChange = async (newStatus: FireStatus) => {
        const updated = await updateFireStatus(reportRef, newStatus);
        if (updated) {
            onStatusChange(updated);
            setSuccess(`Fire marcked as ${newStatus}`);
        }
    };

    const handleContain = () => handleChange('contained');
    const handleExtinguish = () => handleChange('extinguished');
    const handleReactive = () => handleChange('active');

    if (status !== 'verified') {
        return (
            <Card title='Fire Status'>
                <p className='text-text-muted text-sm'>
                    This report needs to be verified before its fire status can be set.
                </p>
            </Card>
        );
    }

    return (
        <Card title='Fire Status'>
            {success && (
                <div role='alert' className='alert bg-status-success/10 border border-status-success/30 text-status-success text-medium mb-2'>
                    <span>{success}</span>
                </div>
            )}
            {error &&
                <div role='alert' className='alert bg-status-error/10 border border-status-error/30 text-status-error text-medium mb-2'>
                    <span>{error}</span>
                </div>
            }

            {fireStatus === 'active' &&
                <div className='flex flex-col gap-3'>
                    <p className='text-text-muted text-sm'>
                        This fire is still shown as active and growing on the live map.
                    </p>
                    <div className='flex gap-2'>
                        <button
                            type='button'
                            className='btn btn-warning btn-sm flex-1 text-lg'
                            onClick={handleContain}
                            disabled={loading}
                        >
                            {loading ? 'Updating...' : 'Mark Contained'}
                        </button>
                        <button
                            type='button'
                            className='btn btn-error btn-sm flex-1 text-lg'
                            onClick={handleExtinguish}
                            disabled={loading}
                        >
                            {loading ? 'Updating' : 'Mark Extinguuished'}
                        </button>
                    </div>
                </div>
            }

            {fireStatus === 'contained' && (
                <div className='flex flex-col gap-3'>
                    <p className='text-text-muted text-sm'>
                        This fire has stopped growing but has not been marked out yet.
                    </p>
                    <div className='flex gap-2'>
                        <button
                            type='button'
                            className='btn btn-error btn-sm flex-1 text-lg'
                            onClick={handleExtinguish}
                            disabled={loading}
                        >
                            {loading ? 'Updating...' : 'Marked Extinguished'}
                        </button>
                        <button
                            type='button'
                            className='btn btn-primary btn-sm flex-1 text-lg'
                            onClick={handleReactive}
                            disabled={loading}
                        >
                            {loading ? 'Updating...' : 'Reactive'}
                        </button>
                    </div>
                </div>
            )}

            {fireStatus === 'extinguished' && (
                <div className='flex flex-col gap-3'>
                    <p className='text-text-muted text-sm'>
                        This fire is marked out and is fading from the live map.
                    </p>
                    <button
                        type='button'
                        className='btn btn-primary btn-sm text-lg'
                        onClick={handleReactive}
                        disabled={loading}
                    >
                        {loading ? 'Updating...' : 'Reactive'}
                    </button>
                </div>
            )}
        </Card>
    );
}
