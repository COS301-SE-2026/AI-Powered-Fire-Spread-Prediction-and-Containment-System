import { useState } from 'react';
import { useSavedLocations } from '../../hooks/useSavedLocations';
import { LocationCard } from './LocationCard';
import { AddLocation } from './AddLocation';
import { LiveMapRef } from '../../lib/SaveLocationMapRef';
import { Skeleton } from '../ui/skeleton/Skeleton';


const MAX_LOCATIONS = 6;

interface SavedLocationsProps {
    role: string;
}

export function SavedLocations({ role }: SavedLocationsProps) {
    const { locations, loading, error, addLocation, removeLocation } = useSavedLocations();
    const [show, setShow] = useState(false);
    const [deleteError, setDeleteError] = useState('');

    async function handleDelete(id: string) {
        setDeleteError('');
        try {
            await removeLocation(id);
        } catch (err) {
            if (err instanceof Error) {
                setDeleteError(err.message);
            } else {
                setDeleteError('Could not delete location.');
            }
        }
    }

    const rows = [];
    for (const location of locations) {
        let href: string | null = null;
        if(location.lat != null && location.lng != null){
            href = LiveMapRef(role, location.lat, location.lng);
        } 
        rows.push(<LocationCard key={location.id} location={location} href={href} onDelete={handleDelete} />);
    }

    let addButton = null;
    if (locations.length < MAX_LOCATIONS){
        addButton = (
            <button type="button" onClick={() => setShow(true)} className="aspect-square rounded-xl border border-dashed border-carbon-stroke text-text-muted flex items-center justify-center hover:bg-carbon-card"> + Add location </button>
        );
    }
    let deleteErrorMessage = null;
    if (deleteError) {
        deleteErrorMessage = <div className='text-error text-sm mb-2'>{deleteError}</div>
    }
    return (
        <div className='w-full rounded-2xl border border-carbon-stroke p-4 flex flex-col'>
            <div className='flex items-baseline gap-2 mb-3'>
                <h2 className='uppercase'>Saved locations</h2>
                <span className='text-base p-2 text-text-muted'>
                    (only upto 6 locations)
                </span>
            </div>
            {error ? <div className='text-error text-sm mb-2'>{error}</div> : null}
            {deleteErrorMessage}
            {loading ? (
                <div role='status' aria-busy='true' className='grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4'>
                    <span className='sr-only'>Loading saved locations</span>
                    {Array.from({ length: 3 }, (_, i) => (
                        <Skeleton key={i} className='h-24 rounded-xl' />
                    ))}
                </div>
            ) : (
                <div className='grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4'>
                    {rows}
                    {addButton}
                </div>
            )}
            {show ? (
                <AddLocation onClose={() => setShow(false)} onSubmit={addLocation} />
            ): null}
        </div>
    );
}