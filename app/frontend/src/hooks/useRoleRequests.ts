import { useState, useEffect } from 'react';
import type { RoleRequest, RoleStatus } from '../types/role-request';

export function useRoleRequests() {
    const [requests, setRequests] = useState<RoleRequest[]>([]);
    const [loading, setLoading] = useState(true);


    useEffect(() => {
        const fetchRequest = async() => {
            try{
                const resp = await fetch(`/api/admin/role-requests`);
                if (!resp.ok) {
                    console.warn("API unavailable");
                    setRequests([])
                    return;
                }
                const data = await resp.json();
                setRequests(data.data ?? []);
            }catch (error){
                console.error("Failed to load role requests", error);
                setRequests([])
            }finally{
                setLoading(false);
            }
        }
        fetchRequest();
    }, []);

    const approveRequest = async (requestId: string) => {
        try{
            const resp = await fetch(`/api/admin/role-requests/${requestId}/approve`, {
                method: 'PUT'
            });

            if(resp.ok){
                const updated = await resp.json();

                setRequests(prev => prev.map(req =>
                    req.request_id === requestId ? updated : req
                ));
            }else{
                console.error("Approval failed");
            }
        }catch(error){
            console.error("Error approving request");
        }
    }

    const rejectRequest = async(requestId: string) => {
        try{
            const resp = await fetch(`/api/admin/role-requests/${requestId}/reject`, {
                method: 'PUT'
            });

            if(resp.ok){
                setRequests(prev => prev.map(req =>
                    req.request_id === requestId ? { ...req, status: 'rejected' as RoleStatus } : req
                ));
            }else{
                console.error("Reject failed:", await resp.text());
            }
        }catch(error){
            console.error("Error rejecting request", error);
        }
    };

    const revokeRequest = async(requestId: string) => {
        try{
            const resp = await fetch(`/api/admin/role-requests/${requestId}/revoke`, {
                method: 'PUT',
            });

            if(resp.ok){
                setRequests(prev => prev.map(req =>
                    req.request_id === requestId ? {...req, status: 'revoked' as RoleStatus} : req
                ));
            }else{
                console.error("Revoke failed:", await resp.text());
            }
        }catch(error){
            console.error("Error revoking request", error);
        }
    };
    return { requests, loading, approveRequest, rejectRequest, revokeRequest };
}
