import { rejects } from "node:assert";
import { resolve } from "node:dns";

const DB_NAME = 'fireaway_offline_db'
const DB_VERSION = 1

export interface OfflineIncident {
    id: string;
    latitude: number;
    longitude: number;
    status: string;
    severity: string;
    report_time: string;
    estimated_size_ha?: number;
}

export interface OfflinePredictionOverlay {
    incident_id: string;
    timestamp: string;
    prediction_grid: {
        type: string;
        features: Array<{
            type: string;
            geometry: {
                type: string;
                coordinates: number[][][] | number[][][][];
            };
            properties: {
                probability: number;
                horizon_hours: number;
            };
        }>;
    };
};

export interface QueuedContainmentAction {
    id: string;
    action_type: 'containment_line' | 'fire_report';
    payload: {
        incident_id?: string;
        coordinates: Array<[number, number]>;
        timestamp: string;
    };
    created_at: number;
}

class OfflineStore {
    private db: IDBDatabase | null = null;

    async init(): Promise<void> {
        if (typeof window === 'undefined') return;

        return new Promise((resolve, reject) => {
            const request = indexedDB.open(DB_NAME, DB_VERSION);

            request.onupgradeneeded = (event) => {
                const db = (event.target as IDBOpenDBRequest).result;

                if (!db.objectStoreNames.contains('incidents')) {
                    db.createObjectStore('incidents', { keyPath: 'id'});
                }

                if (!db.objectStoreNames.contains('predictions')) {
                    db.createObjectStore('predictions', { keyPath: 'incident_id'});
                }

                if (!db.objectStoreNames.contains('action_queue')) {
                    db.createObjectStore('action_queue', { keyPath: 'id'});
                }
            };

            request.onsuccess = (event) => {
                this.db = (event.target as IDBOpenDBRequest).result;
                resolve();
            };

            request.onerror = () => {
                reject(new Error('Failed to initialise IndexedDB offline db.'));
            };
        });
    }
}

