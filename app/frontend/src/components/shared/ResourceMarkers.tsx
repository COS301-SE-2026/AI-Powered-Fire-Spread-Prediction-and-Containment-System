import { Marker } from 'react-map-gl/mapbox';
import type { NearbyResource } from '../../hooks/useNearbyResources';
import { resourceLabel, capacityLabel } from '../../lib/ResourceLabels';
import { RESOURCE_GROUPS, GROUP_BY_RESOURCE } from '../../lib/ResourceGroups';

interface ResourceMarkersProps {
  readonly resources: NearbyResource[];
  readonly selectedResourceId?: string | null;
  readonly onSelectResource?: (r: NearbyResource) => void;
}

export function ResourceMarkers({ resources, selectedResourceId = null, onSelectResource = undefined }: ResourceMarkersProps) {
    return (
        <>
            {resources.map((r) => {
                const selected = r.id === selectedResourceId;
                const {color} = RESOURCE_GROUPS[GROUP_BY_RESOURCE[r.resource]];
                const size = selected ? 36 : 28;

                return (
                    <Marker key={r.id} longitude={r.externalPin.lng} latitude={r.externalPin.lat} anchor="bottom" style={{ zIndex: selected ? 10 : 1 }} onClick={(e) => { e.originalEvent.stopPropagation(); onSelectResource?.(r) }}>
                        <div className={`flex flex-col items-center cursor-pointer ${r.status === 'available' ? '' : 'opacity-50'}`}>
                            <div className="mb-1.5 whitespace-nowrap rounded-mb border-carbon-stroke bg-carbon-bg px-2 py-0.5 text-sm text-text-primary shadow-lg">
                                {resourceLabel(r)} · {capacityLabel(r)}
                            </div>
                            <div className={`flex items-center justify-center border-2 shadow-lg shadow-black/40 ${selected ? 'border-text-primary' : 'border-carbon-stroke'}`} style={{ width: size, height: size, background: color, borderRadius: '50% 50% 50% 0', transform: 'rotate(-45deg)', marginBottom: size * 0.2, }}>
                                <span className="rounded-full bg-carbon-bg" style={{ width: size * 0.3, height: size *  0.3 }} />
                            </div>
                        </div>
                    </Marker>
                );
            })}
        </>
    );
}