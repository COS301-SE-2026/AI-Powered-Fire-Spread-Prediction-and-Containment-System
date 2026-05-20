import React, { useState } from 'react';
import Button from '../Button';
import { ShieldCheck, Mail, Calendar, User, FileText, AlertCircle } from 'lucide-react';

interface RoleRequest {
  id: string;
  fullName: string;
  email: string;
  accountCreated: string;
  dateRequested: string;
  currentRole: string;
  requestedRole: 'Admin';
  justification?: string;
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

  const nameParts = request.fullName.trim().split(' ');
  const displayName =
    nameParts.length >= 2
      ? `${nameParts[0][0]}. ${nameParts.slice(1).join(' ')}`
      : request.fullName;

  return (
    <div className="rounded-2xl bg-carbon-side border border-carbon-stroke backdrop-blur-md shadow-2xl overflow-hidden w-full max-w-md mx-auto">
      <div className="p-5 flex flex-col gap-4">
                
        {/* card header */}
        <div className="border-b border-white/5 pb-3 w-full border-l-2 border-l-ignite pl-3">
            <h2 className="text-sm font-display font-bold tracking-wider text-white uppercase">
                Role request - {displayName}
            </h2>
        </div>

        {/* card body */}
        <div className="flex flex-col gap-4 font-body text-white select-none w-full">
            
            {/* Full name and account created  */}
            <div className="grid grid-cols-2 gap-x-4 gap-y-3">
                <div className="flex gap-2 items-start">
                    <User size={14} className="text-ignite mt-0.5 shrink-0" />
                    <div>
                        <span className="text-[10px] uppercase font-bold tracking-widest text-neutral/40 font-display block mb-0.5">
                            Full Name
                        </span>
                        <p className="text-sm font-semibold text-[#EDEAE5]">{request.fullName}</p>
                    </div>
                </div>

                <div className="flex gap-2 items-start">
                    <Calendar size={14} className="text-ignite mt-0.5 shrink-0" />
                    <div>
                        <span className="text-[10px] uppercase font-bold tracking-widest text-neutral/40 font-display block mb-0.5">
                            Account Created
                        </span>
                        <p className="text-sm font-semibold text-[#EDEAE5]">{request.accountCreated}</p>
                    </div>
                </div>

                {/* email and date requested */}
                <div className="flex gap-2 items-start min-w-0">
                    <Mail size={14} className="text-ignite mt-0.5 shrink-0" />
                    <div className="min-w-0">
                        <span className="text-[10px] uppercase font-bold tracking-widest text-neutral/40 font-display block mb-0.5">
                            Email Address
                        </span>
                        <p className="text-sm font-semibold text-[#EDEAE5] font-mono truncate">{request.email}</p>
                    </div>
                </div>

                <div className="flex gap-2 items-start">
                    <Calendar size={14} className="text-ignite mt-0.5 shrink-0" />
                    <div>
                        <span className="text-[10px] uppercase font-bold tracking-widest text-neutral/40 font-display block mb-0.5">
                            Date Requested
                        </span>
                        <p className="text-sm font-semibold text-[#EDEAE5]">{request.dateRequested}</p>
                    </div>
                </div>
            </div>

            <div className="border-t border-white/5" />

            {/* requested role */}
            <div className="flex gap-2 items-start">
                <ShieldCheck size={14} className="text-torch mt-0.5 shrink-0" />
                <div>
                    <span className="text-[10px] uppercase font-bold tracking-widest text-neutral/40 font-display block mb-1">
                        Requested Role
                    </span>
                    <span className="inline-flex items-center bg-success/20 border border-success/30 text-success-content text-[11px] font-bold px-2.5 py-0.5 rounded uppercase tracking-wider font-mono">
                        {request.requestedRole}
                    </span>
                </div>
            </div>

            {/* justification */}
            <div className="flex flex-col gap-1.5">
                <div className="flex items-center gap-2">
                    <FileText size={14} className="text-ignite shrink-0" />
                    <span className="text-[10px] uppercase font-bold tracking-widest text-neutral/40 font-display">
                        Justification
                    </span>
                </div>
                <div className="w-full rounded-lg bg-carbon-bg/60 border border-carbon-stroke px-3 py-2.5 min-h-[56px] flex items-center">
                    {request.justification ? (
                        <p className="text-xs leading-relaxed text-[#EDEAE5]/80">{request.justification}</p>
                    ) : (
                        <p className="text-xs italic text-neutral/30">No operational reason listed by applicant.</p>
                    )}
                </div>
            </div>

            {/* buffering */}
            {errorMsg && (
                <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-error/10 border border-error/20 text-error-content text-xs">
                    <AlertCircle size={13} className="shrink-0" />
                    <span>{errorMsg}</span>
                </div>
            )}
        </div>

        {/* Buttons */}
        <div className="flex items-center justify-between gap-3 pt-3 border-t border-white/5 w-full">
            <Button
                variant="ghost"
                disabled={loading}
                onClick={() => handleRoleAction('reject')}
                className="flex-1 h-10 text-xs uppercase tracking-wider font-display border border-white/10 hover:bg-white/5 text-white/70 hover:text-white rounded-md transition-all"
                data-testid="admin-role-change-reject-btn"
            >
                {loading ? <span className="loading loading-spinner loading-xs"></span> : 'Reject'}
            </Button>
            
            <Button
                variant="fire"
                disabled={loading}
                onClick={() => handleRoleAction('approve')}
                className="flex-1 h-10 text-xs uppercase tracking-wider font-display bg-ignite hover:bg-ignite/90 text-white rounded-md shadow-lg shadow-ignite/20 transition-all"
                data-testid="admin-role-change-approve-btn"
            >
                {loading ? <span className="loading loading-spinner loading-xs"></span> : 'Approve'}
            </Button>
        </div>

      </div>
    </div>
  );
};



