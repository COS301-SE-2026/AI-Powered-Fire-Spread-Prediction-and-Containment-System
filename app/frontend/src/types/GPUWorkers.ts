export type Status =
    "active" |
    "busy" |
    "offline" |
    "rejected" |
    "quarantined" |
    "deactivated" |
    "removed";


export interface GPUWorker{
    id: string;
    user_id: string;
    label: string;
    gpu_name: string;
    vram_mb: number;
    driver_version: string | null;
    status: Status;
    consecutive_failures: number;
    quarantine_until: string | null;
    last_heartbeat: string | null;
    activated_at: string;
    deactivated_at: string | null;
    removed_at: string | null;
    removal_reason: string | null;
};