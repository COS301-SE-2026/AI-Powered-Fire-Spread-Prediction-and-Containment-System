export type Resource = 'water_tank' | 'borehole' | 'trailer' | 'dam' | 'aircraft' | 'crew' | 'other';

export type Capacity = 'liters' | 'members' | 'other';

export type Status = 'available' | 'dispatched' | 'unavailable';

export interface ResourceTable {
    id: string;
    resource: Resource;
    otherResource: string;
    capacity: number;
    capacityUnit: Capacity;
    otherCapacity: string;
    status: Status;
    availableFrom: string;
    availableUntil: string | null;
    location: string;
    externalPin: { lat: number; lng: number };
    name: string;
    contact: string;
}

export interface ResourceList {
    data: ResourceTable[];
    total: number;
}

export type ResourceInput = Omit<ResourceTable, 'id' | 'status' | 'capacityUnit'>
