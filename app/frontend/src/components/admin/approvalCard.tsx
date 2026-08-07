import React, { useState } from 'react';
import Card from '../Card';

interface RoleRequest {
  id: string;
  email: string;
  currentRole: string;
  requestedRole: 'Admin';
}

interface AdminApprovalCardProps {
  request: RoleRequest;
  onActionComplete: (requestId: string, status: 'approved' | 'rejected') => void;
}

export const AdminApprovalCard: React.FC<AdminApprovalCardProps> = ({ request, onActionComplete }) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleRoleAction = async (action: 'approve' | 'reject') => {
    setLoading(true);
    setErrorMsg(null);

    try {
      const response = await fetch(`http://localhost:3000/api/admin/roles/${request.id}/${action}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Role change approval card fetching rejected by gateway API. Status code: ${response.status}`);
      }

      onActionComplete(request.id, action === 'approve' ? 'approved' : 'rejected');
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMsg(err.message);
      } else {
          setErrorMsg('Unknown error with approving role changes');
      }
    } finally {
      setLoading(false);
    }
  };

  let rejectLabel: React.ReactNode;
  let approveLabel: React.ReactNode;

  if (loading) {
    rejectLabel = <span className="loading loading-spinner loading-xs" />;
    approveLabel = <span className="loading loading-spinner loading-xs" />;
  } else {
    rejectLabel = 'Reject';
    approveLabel = 'Approve';
  }

  const cardActionButtons = (
    <>
      <button
        type="button"
        className="btn btn-ghost h-11 min-h-11 px-4"
        disabled={loading}
        onClick={() => handleRoleAction('reject')}
        data-testid="admin-role-change-reject-btn"
      >
        {rejectLabel}
      </button>

      <button
        type="button"
        className="btn btn-primary h-11 min-h-11 px-4"
        disabled={loading}
        onClick={() => handleRoleAction('approve')}
        data-testid="admin-role-change-approve-btn"
      >
        {approveLabel}
      </button>
    </>
  );

  return (
    <Card
      title={`Request ID: ${request.id.slice(0, 8)}`}
      actions={cardActionButtons}
    >
      <div className="flex flex-col space-y-3 font-sans">
        {/*Email*/}
        <div>
          <span className="text-[11px] uppercase font-bold tracking-wider text-slate-400 block">User Email</span>
          <p className="text-sm font-semibold text-slate-800 font-mono truncate">{request.email}</p>
        </div>

        {/*Roles*/}
        <div className="grid grid-cols-2 gap-2 pt-1">
          <div className="bg-base-200/50 p-2 rounded border border-base-200">
            <span className="text-[10px] uppercase font-bold text-slate-400 block">Current Role</span>
            <span className="text-xs font-bold text-slate-600">{request.currentRole}</span>
          </div>
          <div className="bg-[#E84500]/5 p-2 rounded border border-[#E84500]/20">
            <span className="text-[10px] uppercase font-bold text-[#E84500] block">Requested Role</span>
            <span className="text-xs font-black text-[#E84500] animate-pulse"> {request.requestedRole}</span>
          </div>
        </div>

        {/*Error*/}
        {errorMsg && (
          <div className="">
            <span>{errorMsg}</span>
          </div>
        )}
      </div>
    </Card>
  );
};

