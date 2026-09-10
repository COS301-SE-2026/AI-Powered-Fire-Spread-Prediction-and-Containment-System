import React, { useState } from 'react';
import type { RoleRequest, RoleStatus } from '../../types/RoleRequest';
import { useRoleRequests } from '../../hooks/useRoleRequests';
import { useRotate } from '../../hooks/useRotate';
import { RoleApprovalModal } from '../../components/admin/approvalModal';
import { AdminSideBar } from '../../components/admin/AdminSideBar';
import { RoleFilterTabs } from '../../components/admin/approvalFilter';
import { RoleRequestsTable } from '../../components/admin/approvalTable';
import { RotateHint } from '../../components/shared/RotateHint';
import { PageHeader } from '../../components/layout/pageHeader';

export default function RoleApprovalPage() {
  const { requests, loading, approveRequest, rejectRequest, revokeRequest } = useRoleRequests();
  const [selectedRequest, setSelectedRequest] = useState<RoleRequest | null>(null);
  const [filter, setFilter] = useState<'All' | RoleStatus>('All');
  const { showHint, dismiss } = useRotate();

  const handleApprove = async (requestId: string) => {
    await approveRequest(requestId);
    setSelectedRequest(null);
  };

  const handleReject = async (requestId: string) => {
    await rejectRequest(requestId);
    setSelectedRequest(null);
  };

  const handleRevoke = async (requestId: string) => {
    await revokeRequest(requestId);
    setSelectedRequest(null);
  };

  if (loading) {
    return (
      <AdminSideBar hideLoginRegister>
        <div className="p-6 flex justify-center items-center min-h-[60vh]">
          <span className="loading loading-spinner loading-lg text-primary" />
        </div>
      </AdminSideBar>
    );
  }
  return (
    <AdminSideBar hideLoginRegister>
      <div className="p-2 md:p-6 flex flex-col h-full w-full">
        <RotateHint show={showHint} onDismiss={dismiss} />
        {/* Header + filter */}
        <PageHeader title="Role Approvals" subtitle="Manage user role requests" showIcons />

        <RoleFilterTabs filter={filter} onChange={setFilter} />

        {/* table */}
        <div className='flex-1 min-h-0'>
          <RoleRequestsTable requests={requests} filter={filter} onView={setSelectedRequest} />
        </div>

        {/* modal overlay */}
        {selectedRequest && (
          <RoleApprovalModal
            request={selectedRequest}
            onClose={() => setSelectedRequest(null)}
            onApprove={handleApprove}
            onReject={handleReject}
            onRevoke={handleRevoke}
          />
        )}
      </div>
    </AdminSideBar>
  );
}
