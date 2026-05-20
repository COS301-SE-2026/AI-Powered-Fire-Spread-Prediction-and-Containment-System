import { UserStar } from 'lucide-react';
import React, { useState, useEffect } from 'react';

interface RoleRequest {
    request_id: string;
    user_id: string;
    role: 'user' | 'admin' | 'firefighter';
    status: 'pending' | 'approved' | 'rejected';

}

export default function RoleApprovalPage() {
    const [request, setRequest] = useState<RoleRequest[]>([]);
    const [selectedRequest, setSelectedRequest] = useState<RoleRequest | null>(null);
    const [filter, setFilter] = useState<'All' | 'Pending' | 'Rejected' | 'Revoked'>('All');

    useEffect(() => {
        const fetchRequest = async() => {
            try{
                const resp = await fetch('/api/admin/roles/role-request');
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
            const resp = await fetch(`/api/admin/roles/role-request/${requestId}/approve`, {
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
            const resp = await fetch(`/api/admin/roles/role-request/${requestId}/rejected`, {
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
                <div className="fixed inset-0 bg-black/50 flex items-center z-50">
                    <div>
                        {/* modal content */}
                        <div className="flex justify-end gap-2 mt-4">
                            <button onClick={() => handleReject(selectedRequest.request_id)}>Reject</button>
                            <button onClick={() => handleApprove(selectedRequest.request_id)}>Approve</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}