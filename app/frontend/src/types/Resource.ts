export type Resource = 'water_tank' | 'borehole' | 'trailer' | 'dam' | 'aircraft' | 'crew' | 'other';

export type Capacity = 'liters' | 'members';

export type Status = 'available' | 'dispatched' | 'unavailable';

export interface ResourceTable {
    id: string;
    resource: Resource;
    other: string | null;
    capacity: Capacity;
    capacity_value: number;
    capacity_other: string | null;
    status: Status;
    available_from: string;
    available_until: string | null;
    lat: number;
    lng: number;
    location_text: string;
    owner_name: string;
    owner_contact: string;
    fire_ref: string | null;
}

export interface ResourceList {
    data: ResourceTable[];
    total: number;
}
