import type { ResourceTable, Resource, Status } from '../types/Resource';

const RESOURCE_LABEL: Record<Resource, string> = {
    water_tank: 'Water Tank',
    borehole: 'Borehole',
    trailer: 'Trailer',
    dam: 'Dam',
    aircraft: 'Aircraft',
    crew: 'Crew',
    other: 'Other',
}

export const STATUS_LABEL: Record<Status, { label: string; className: string}> = {
    available: { label: 'Available', className: 'text-text-success' },
    dispatched: { label: 'Dispatched', className: 'text-text-primary' },
    unavailable: { label: 'Unavailable', className: 'text-text-muted' },
}

export function resourceLabel(r: ResourceTable): string {
    return r.resource === 'other' && r.otherResource ? r.otherResource : RESOURCE_LABEL[r.resource];
}

export function capacityLabel(r: ResourceTable): string {
    const amount = r.capacity.toLocaleString('en-ZA');
    if (r.capacityUnit === 'liters') return `${amount} L`;
    if (r.capacityUnit === 'members') return `${amount} mambers`;
    return r.otherCapacity ? `${amount} ${r.otherCapacity}` : amount;
}