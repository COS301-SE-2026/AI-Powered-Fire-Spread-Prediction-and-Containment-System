//manages and stores offline fire incidents in cache

const DB_NAME = 'fireaway_offline_db'
const DB_VERSION = 1

export interface FireReportMapResponse {
    id: string;
    reference_number: string;
    lat: number;
    lng: number;
    location_text: string;
    status: string;
    boundary_radius: number;
    size: number;
    submitted_at: string;
    reporter_name?: string | null;
}

export interface CreateContainmentLine {
    wkt: string;
}

export interface FireReportCreate {
    lat: number;
    lng: number;
    location_text: string;
    description?: string | null;
    image_url?: string | null;
    boundary_radius: number;
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
                coordinates: number[][][] | number [][][][];
            };
            properties: {
                probability: number;
                horizon_hours: number;
            };
        }>;
    };
}

export type QueuedContainmentPayload = CreateContainmentLine;
export type QueuedFireReportPayload = FireReportCreate;

export interface QueuedContainmentAction {
    id: string;
    action_type: 'containment_line';
    payload: QueuedContainmentPayload;
    created_at: number;
}

export interface QueuedReportAction {
    id: string;
    action_type: 'fire_report';
    payload: QueuedFireReportPayload;
    created_at: number;
}

export type QueuedAction = QueuedContainmentAction | QueuedReportAction;

function coordinatesToWKT(points: Array<[number, number]>): string {
    const lineStringPoints = points.map(([lng, lat]) => `${lng} ${lat}`).join(', ');
    return `LINESTRING(${lineStringPoints})`;
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

    async cacheIncidents(incidents: FireReportMapResponse[]): Promise<void> {
        if (!this.db) await this.init();
        if (!this) return;

        //t_action stands for transaction, transaction is a method though. So I needed to change oit to something else
        //like it would've  been fine, but maybe confusing.
        const t_action = this.db.transaction('predictions', 'readwrite');
        const store = t_action.objectStore('predictions');
        store.clear();

        for (const incident of incidents) {
            store.put(incident);
        }

        return new Promise((resolve, reject) => {
            t_action.oncomplete = () => resolve();
            t_action.onerror = () => reject(t_action.error);
        });
    }

    async getCachedIncidents(): Promise<FireReportMapResponse[]> {
        if (!this.db) await this.init();
        if (!this) return [];

        return new Promise((resolve, reject) => {
            const t_action = this.db!.transaction('incidents', 'readonly');
            const store = t_action.objectStore('incidents');
            const request = store.getAll();

            request.onsuccess = () => resolve(request.result || []);
            request.onerror = () => reject(request.error);
        });
    }    

    async cachePredictionOverlay(prediction: OfflinePredictionOverlay): Promise<void> {
        if (!this.db) await this.init();
        if (!this) return;

        const t_action = this.db.transaction('predictions', 'readwrite');
        const store = t_action.objectStore('predictions');
        store.put(prediction);

        return new Promise((resolve, reject) => {
            t_action.oncomplete = () => resolve();
            t_action.onerror = () => reject(t_action.error);
        });
    }

    async getCachedPredictionOverlay(incidentId: string): Promise<OfflinePredictionOverlay | null> {
        if (!this.db) await this.init();
        if (!this) return null;

        return new Promise((resolve, reject) => {
            const t_action = this.db!.transaction('predictions', 'readonly');
            const store = t_action.objectStore('predictions');
            const request = store.get(incidentId);

            request.onsuccess = () => resolve(request.result || null);
            request.onerror = () => reject(request.error);
        });
    }
    
    private async queueRawAction(action:Omit<QueuedAction, 'id' | 'created_at'>): Promise<string> {
        if (!this.db) await this.init();
        if (!this) throw new Error('IndexedDB not ready');

        const id = (typeof crypto !== 'undefined' && crypto.randomUUID)
        ? crypto.randomUUID()
        : String(Date.now());

        const record = {
            ...action,
            id,
            created_at: Date.now(),
        };

        return new Promise((resolve, reject) => {
            const t_action = this.db!.transaction('action_queue', 'readwrite');
            const store = t_action.objectStore('action_queue');
            const request = store.add(record);

            request.onsuccess = () => resolve(id);
            request.onerror = () => reject(request.error);
        });
    }

    async queueContainmentLine(points: Array<[number, number]>): Promise<string> {
        const payload:CreateContainmentLine = {
            wkt: coordinatesToWKT(points),
        };

        return this.queueRawAction({
            action_type: 'containment_line',
            payload,
        });
    }

    async queueFireReport(report: FireReportCreate): Promise<string> {
        return this.queueRawAction({
            action_type: 'fire_report',
            payload: report,
        });
    }

    async getQueuedActions(): Promise<QueuedAction[]> {
        if (!this.db) await this.init();
        if (!this) return [];

        return new Promise((resolve, reject) => {
            const t_action = this.db!.transaction('action_queue', 'readonly');
            const store = t_action.objectStore('action_queue');
            const request = store.getAll();

            request.onsuccess = () => resolve(request.result || []);
            request.onerror = () => reject(request.error);
        });
    }

    async removeQueueAction(id: string): Promise<void> {
        if (!this.db) await this.init();
        if (!this) return;

        return new Promise((resolve, reject) => {
            const t_action = this.db!.transaction('action_queue', 'readwrite');
            const store = t_action.objectStore('action_queue');
            const request = store.delete(id);

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    async syncQueuedActions(apiBaseUrl: string): Promise<{ syncedCount: number; errors: number}> {
        const queue = await this.getQueuedActions();
        let syncedCount = 0;
        let errors = 0;

        for (const item of queue) {
            try {
                let endpoint = `${apiBaseUrl}/api/v1/containment-lines`;
                if (item.action_type === 'fire_report') {
                    endpoint = `${apiBaseUrl}/api/reports`;
                }

                const response = await fetch(endpoint, {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(item.payload),
                });

                if (response.ok) {
                    await this.removeQueueAction(item.id);
                    syncedCount++;
                } else {
                    errors++;
                }
            } catch {
                errors++;
            }
        }
        return { syncedCount, errors };
    }
}

export const offlineStore = new OfflineStore();

