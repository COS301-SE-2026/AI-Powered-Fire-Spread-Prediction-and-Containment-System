import Link from 'next/link';
import { X } from 'lucide-react';
import type { SavedLocation } from "../../types/SavedLocation";

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;
const PREVIEW_ZOOM = 14;

function buildPreviewUrl(lat: number, lng: number): string {
  return `https://api.mapbox.com/styles/v1/mapbox/navigation-night-v1/static/pin-s+fd5d19(${lng},${lat})/${lng},${lat},${PREVIEW_ZOOM},0/400x200@2x?access_token=${MAPBOX_TOKEN}`;
}

interface LocationCardProps {
    location: SavedLocation;
    href: string | null;
    onDelete: (id: string) => void;
}

export function LocationCard({ location, href, onDelete }: LocationCardProps) {
    const hasCoords = location.lat != null && location.lng != null;
    let preview = <span className="text-text-muted text-sm">No Map Preview</span>;
    if (hasCoords) {
        preview = <img src={buildPreviewUrl(location.lat as number, location.lng as number)} alt={`Map preview of ${location.label}`} className='w-full h-full object-cover' />
    } 

    let overlay = null;
    if(href !== null){
        overlay = <Link href={href} aria-label={`Open ${location.label} on the live map`} className='absolute inset-0 rounded-xl' />;
    }
    return (
        <div className="relative aspect-square flex flex-col rounded-xl border border-carbon-stroke p-2 flex flex-col sm:aspect-square">
            <div className="h-32 sm:h-auto flex-1 min-h-0 rounded-lg border border-carbon-stroke bg-carbon-card mb-3 overflow-hidden flex items-center justify-center">
                {preview}
                <button type="button" onClick={() => onDelete(location.id)} aria-label={`Delete ${location.label}`} title="Delete location" className="absolute top-1.5 right-1.5 z-10 size-7 rounded-full bg-carbon-bg/80 border border-carbon-stroke text-text-muted flex items-center justify-center hover:text-text-primary active:scale-95 transition cursor-pointer">
                    <X className="size-4" />
                </button>
            </div>
            <span className="font-bold text-text-primary">{location.label}</span>
            <span className="text-text-muted text-sm mt-1">{location.address}</span>
            {overlay}
        </div>
    );
}