import { useState } from 'react';
import { useSavedLocations } from '../../hooks/useSavedLocations';
import { LocationCard } from './LocationCard';
import { AddLocation } from './AddLocation';

export function SavedLocations() {
    const { locations, loading, error, addLocation } = useSavedLocations();
    const [show, setShow] = useState(false);

    const rows = [];
    for (const location of locations) {
        rows.push(<LocationCard key={location.id} location={location} />);
    }
    return (
        <div className='w-full rounded-2xl border border-carbon-stroke p-4 flex flex-col'>
            <h2 className='uppercase mb-3'>Saved locations</h2>
            {error ? <div className='text-error text-sm mb-2'>{error}</div> : null}
            {loading ? (
                <div className='flex justify-center items-center min-h-[20vh]'>
                    <span className="loading loading-spinner loading-lg text-primary" />
                </div>
            ) : (
                <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
                    {rows}
                    <button type="button" onClick={() => setShow(true)} className="rounded-xl border border-dashed border-carbon-stroke text-text-muted flex items-center justify-center min-h-[10rem] hover:bg-carbon-card">+ Add location</button>
                </div>
            )}
            {show ? (
                <AddLocation onClose={() => setShow(false)} onSubmit={addLocation} />
            ): null}
        </div>
    );
}