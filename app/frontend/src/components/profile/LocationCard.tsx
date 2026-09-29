import type { SavedLocation } from "../../types/SavedLocation";

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;
const PREVIEW_ZOOM = 14;

function buildPreviewUrl(lat: number, lng: number): string {
  return `https://api.mapbox.com/styles/v1/mapbox/navigation-night-v1/static/pin-s+fd5d19(${lng},${lat})/${lng},${lat},${PREVIEW_ZOOM},0/400x200@2x?access_token=${MAPBOX_TOKEN}`;
}

interface LocationCardProps {
    location: SavedLocation;
}

export function LocationCard({ location }: LocationCardProps) {
    const hasCoords = location.lat != null && location.lng != null;
    return (
        <div className="rounded-xl border border-carbon-stroke p-3 flex flex-col">
            <div className="rounded-lg border border-carbon-stroke bg-carbon-card h-32 mb-3 overflow-hidden flex items-center justify-center">
                {hasCoords ? (
                    <img src={buildPreviewUrl(location.lat as number, location.lng as number)} alt={`Map preview of ${location.label}`} className='w-full h-full object-cover' />
                ) : (
                    <span className="text-text-muted text-sm">No Map Preview</span>
                )}
            </div>
            <span className="font-bold text-text-primary">{location.label}</span>
            <span className="text-text-muted text-sm mt-1">{location.address}</span>
        </div>
    );
}