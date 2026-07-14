import React, { useState, useEffect } from 'react';
import type { RoleRequest,RoleStatus } from '../../types/admin';
import { RoleApprovalModal } from '../../components/admin/approvalModal';
import { SideBarLayout } from '../../components/demoSidebar';
import { RoleFilterTabs } from '../../components/admin/approvalFilter';
import { RoleRequestsTable } from '../../components/admin/approvalTable';
import { API_BASE_URL } from '../../config/api';

export default function RoleApprovalPage() {
    const [request, setRequest] = useState<RoleRequest[]>([]);
    const [selectedRequest, setSelectedRequest] = useState<RoleRequest | null>(null);
    const [filter, setFilter] = useState<'All' | RoleStatus>('All');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchRequest = async() => {
            const url = `/api/admin/role-requests`;
            console.log('Fetching from:', url);
            try{
                const resp = await fetch(`/api/admin/role-requests`);
                if (!resp.ok) {
                    console.warn("API unavailable");
                    setRequest([])
                    return;
                }
                const data = await resp.json();
                setRequest(data.data ?? []);
            }catch (error){
                console.error("Failed to load role requests", error);
                setRequest([])
            }finally{
                setLoading(false);
            }
        }
        fetchRequest();
    }, []);

    const handleApprove = async (requestId: string) => {
        try{
            const resp = await fetch(`/api/admin/role-requests/${requestId}/approve`, {
                method: 'PUT'
            });

            if(resp.ok){
                const updateRequest = await resp.json();

                setRequest(prev => prev.map(req => 
                    req.request_id === requestId ? updateRequest : req
                ));

                setSelectedRequest(null); // close modal
            }else{
                console.error("Approval failed");
            }
        }catch(error){
            console.error("Error approving request");
        }
    }

    const handleReject = async(requestId: string) => {
        try{
            const resp = await fetch(`/api/admin/role-requests/${requestId}/reject`, {
                method: 'PUT'
            });

            if(resp.ok){
                setRequest(prev => prev.map(req => 
                    req.request_id === requestId ? { ...req, status: 'rejected' as RoleStatus } : req
                ));
                setSelectedRequest(null);
            }else{
                console.error("Reject failed:", await resp.text());
            }
        }catch(error){
            console.error("Error rejecting request", error);
        }
    };

    const handleRevoke = async(requestId: string) => {
        try{
            const resp = await fetch(`/api/admin/role-requests/${requestId}/revoke`, {
                method: 'PUT',
            });

            if(resp.ok){
                setRequest(prev => prev.map(req => 
                    req.request_id === requestId ? {...req, status: 'revoked' as RoleStatus} : req
                ));
                setSelectedRequest(null)
            }else{
                console.error("Revoke failed:", await resp.text());
            }
        }catch(error){
            console.error("Error revoking request", error);
        }
    };

    if (loading) {
        return (
            <SideBarLayout>
                <div className="p-6 flex justify-center items-center min-h-[60vh]">
                    <span className="loading loading-spinner loading-lg text-primary"></span>
                </div>
            </SideBarLayout>
        );
    }
    return(
        <SideBarLayout>
            <div className="p-6 flex flex-col h-full w-full">
                {/* Header + filter */}
                <header className="mb-6">
                    <h1 className="text-3xl font-display font-bold tracking-wider text-neutral uppercase">Role Approvals</h1>
                    <p className="text-sm text-neutral/50 font-medium">Manage user role requests</p>
                </header>

                <RoleFilterTabs filter={filter} onChange={setFilter}/>

                {/* table */}
                <RoleRequestsTable requests={request} filter={filter} onView={setSelectedRequest} />

                {/* modal overlay */}
                {selectedRequest && (
                    <RoleApprovalModal request={selectedRequest} onClose={() => setSelectedRequest(null)} onApprove={handleApprove} onReject={handleReject} onRevoke={handleRevoke}/>
                )}
            </div>
        </SideBarLayout>
    );
}