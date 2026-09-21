import { Droplets, Truck, Users, Plane, Package } from 'lucide-react';
import type { Resource } from '../types/Resource';

export const RESOURCE_GROUPS = {
    water: { label: 'Water', color: 'var(--color-info)', icon: Droplets },
    trailer: { label: 'Trailer', color: 'var(--color-torch)', icon: Truck },
    crew: { label: 'Crew', color: 'var(--color-success)', icon: Users },
    aircraft: { label: 'Aircraft', color: 'var(--color-primary)', icon: Plane },
    other: { label: 'Other', color: 'var(--color-text-muted)', icon: Package },
}

export type ResourceGroup = keyof typeof RESOURCE_GROUPS;

export const GROUP_BY_RESOURCE: Record<Resource, ResourceGroup> = {
    water_tank: 'water',
    borehole: 'water',
    dam: 'water',
    trailer: 'trailer',
    crew: 'crew',
    aircraft: 'aircraft',
    other: 'other',
};