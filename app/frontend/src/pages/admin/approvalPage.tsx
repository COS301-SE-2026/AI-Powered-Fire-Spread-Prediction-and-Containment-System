import { UserStar } from 'lucide-react';
import React, { useState, useEffect } from 'react';
import type { RoleRequest } from '../../types/admin';
import { RoleApprovalModal } from '../../components/admin/approvalModal';

export default function RoleApprovalPage() {
    const [request, setRequest] = useState<RoleRequest[]>([]);
    const [selectedRequest, setSelectedRequest] = useState<RoleRequest | null>(null);
    const [filter, setFilter] = useState<'All' | 'Pending' | 'Rejected' | 'Revoked'>('All');

    useEffect(() => {
        const fetchRequest = async() => {
            try{
                const resp = await fetch('/api/admin/roles/role-requests');
                const data = await resp.json();
                setRequest(data);
            }catch (error){
                console.error("Failed to load role requests", error);
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

    return(
        <div className="p-6 flex flex-col h-full w-full">
            {/* Header + filter */}

            {/* table */}

            {/* modal overlay */}
            {selectedRequest && (
                <RoleApprovalModal request={selectedRequest} onClose={() => setSelectedRequest(null)} onApprove={handleApprove} onReject={handleReject}/>
            )}
            <button onClick={() => setSelectedRequest({ request_id: 'req_1', user_id: 'user_1', user_full_name: "James Smith", role: 'firefighter', status: 'pending' })}>
                Test Modal
            </button>
        </div>
    );
}