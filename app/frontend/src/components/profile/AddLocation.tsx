import { useState } from 'react';
import type { SavedLocationCreate } from '../../types/SavedLocation';
import { LocationField } from '../reportfire/LocationField';
import { LOCATION_PLACEHOLDER } from '../reportfire/locationConstants';


interface AddLocationProps {
    onClose: () => void;
    onSubmit: (payload: SavedLocationCreate) => Promise<void>;
}

export function AddLocation({ onClose, onSubmit }: AddLocationProps) {
    const [label, setLabel] = useState('');
    const [address, setAddress] = useState(LOCATION_PLACEHOLDER);
    const [pin, setPin] = useState<{ lat: number; lng: number } | null>(null);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState('');

    function handleLocationChange(val: string) {
        setAddress(val);
    }

    function handleLocationSelect(loc: { lat: number; lng: number; address: string }) {
        setAddress(loc.address);
        setPin({ lat: loc.lat, lng: loc.lng });
    }

    async function handleSubmit(event: React.FormEvent) {
        event.preventDefault();
        if(!label.trim() || !pin) {
            setError('Label and address are required.');
            return;
        }
        setSubmitting(true);
        setError('');
        try {
            await onSubmit({ label: label.trim(), address: address.trim(), lat: pin.lat, lng: pin.lng, });
            onClose();
        } catch (err) {
            if (err instanceof Error) {
                setError(err.message);
            } else {
                setError('Could not save location.');
            }
        } finally {
            setSubmitting(false);
        }
    }
    return (
        <div className='fixed inset-0 bg-black/60 flex items-center justify-center z-50'>
            <div className='rounded-2xl border border-carbon-stroke bg-carbon-card p-6 w-full max-w-lg'>
                <h3 className='uppercase mb-4'>Add location</h3>
                <form onSubmit={handleSubmit} className='flex flex-col gap-3'>
                    <input type="text" placeholder="Label (e.g. Home)" value={label} onChange={(e) => setLabel(e.target.value)} className="carbon-input" />
                    <LocationField value={address} onChange={handleLocationChange} onValidSelect={handleLocationSelect} />
                    {error ? <span className='text-error text-sm'>{error}</span> :null}
                    <div className='flex justify-end gap-2 mt-2'>
                        <button type="button" onClick={onClose} className="text-text-muted px-3 py-2">Cancel</button>
                        <button type="submit" disabled={submitting} className="bg-ignite text-char px-4 py-2 rounded-lg font-bold">{submitting ? 'Saving...' : 'Save'}</button>
                    </div>
                </form>
            </div>
        </div>
    );
}