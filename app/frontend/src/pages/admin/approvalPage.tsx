import React, { useState, useEffect } from 'react';
import type { RoleRequest,RoleStatus } from '../../types/admin';
import { RoleApprovalModal } from '../../components/admin/approvalModal';
import { SideBarLayout } from '../../components/demoSidebar';
import { RoleFilterTabs } from '../../components/admin/approvalFilter';
import { RoleRequestsTable } from '../../components/admin/approvalTable';

const mockRequests: RoleRequest[] = [
    { request_id: 'req_1', user_id: 'user_1', user_full_name: 'James Smith', email: 'j.smith@email.com', role: 'firefighter', status: 'pending', created_at: '2026-05-20T09:12:00Z', firefighter_license_id: 'FF-1001' },
    { request_id: 'req_2', user_id: 'user_2', user_full_name: 'Anna Dlamini', email: 'a.dlamini@email.com', role: 'admin', status: 'pending', created_at: '2026-05-19T14:30:00Z' },
    { request_id: 'req_3', user_id: 'user_3', user_full_name: 'Peter Nkosi', email: 'p.nkosi@email.com', role: 'firefighter', status: 'approved', created_at: '2026-05-18T11:00:00Z', firefighter_license_id: 'FF-1002' },
    { request_id: 'req_4', user_id: 'user_4', user_full_name: 'Lerato Botha', email: 'l.botha@email.com', role: 'admin', status: 'rejected', created_at: '2026-05-17T08:45:00Z' },
    { request_id: 'req_5', user_id: 'user_5', user_full_name: 'Thabo Mokoena', email: 't.mokoena@email.com', role: 'firefighter', status: 'revoked', created_at: '2026-05-16T10:20:00Z', firefighter_license_id: 'FF-2001' },
];


export default function RoleApprovalPage() {
    const [request, setRequest] = useState<RoleRequest[]>([]);
    const [selectedRequest, setSelectedRequest] = useState<RoleRequest | null>(null);
    const [filter, setFilter] = useState<'All' | RoleStatus>('All');

    useEffect(() => {
        const fetchRequest = async() => {
            try{
                const resp = await fetch('/api/admin/roles/role-requests');
                if (!resp.ok) {
                    console.warn("API unavailable, using mock data");
                    setRequest(mockRequests);
                    return;
                }
                const data = await resp.json();
                setRequest(data); 
            }catch (error){
                console.error("Failed to load role requests", error);
                setRequest(mockRequests);
            }
        }
        fetchRequest();
    }, []);

    const handleApprove = async (requestId: string) => {
        try{
            const resp = await fetch(`/api/admin/roles/role-requests/${requestId}/approve`, {
                method: 'POST'
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
            const resp = await fetch(`/api/admin/roles/role-requests/${requestId}/reject`, {
                method: 'POST'
            });

            if(resp.ok){
                const updateRequest = await resp.json();

                setRequest(prev => prev.map(req => 
                    req.request_id === requestId ? updateRequest : req
                ));
                setSelectedRequest(null);
            }
        }catch(error){
            console.error("Error rejecting request:", error);
        }
    };

    const handleRevoke = async(requestId: string) => {
        try{
            const resp = await fetch(`/api/admin/roles/role-requests/${requestId}/revoke`, {
                method: 'POST',
            });

            if(resp.ok){
                setRequest(prev => prev.filter(req => 
                    req.request_id !== requestId
                ));
                setSelectedRequest(null);
            }else{
                console.error('revoke failed');
            }
        }catch(error){
            console.error('error revoking access', error);
        }
    };

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