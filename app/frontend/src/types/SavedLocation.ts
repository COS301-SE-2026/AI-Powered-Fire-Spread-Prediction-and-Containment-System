export interface SavedLocation {
    id: string;
    label: string;
    address: string;
    lat: number | null;
    lng: number | null;
    created_at: string;
}

export interface SavedLocationCreate {
    label: string;
    address: string;
    lat?: number | null;
    lng?: number | null;
}

export interface SavedLocationUpdate {
    label?: string;
    address?: string;
    lat?: number | null;
    lng?: number | null;
}