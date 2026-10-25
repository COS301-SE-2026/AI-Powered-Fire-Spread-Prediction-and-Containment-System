import { X } from 'lucide-react';
import { RoleRequest, UserSummary } from '../../types/RoleRequest';
import { RoleStatusBadge } from './RoleStatusBadge';
import { ScoreBadge } from './ScoreBadge';

interface RoleApprovalModalProps {
  request: RoleRequest;
  onClose: () => void;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
  onRevoke: (id: string) => void;
}

function getReportBreakdown(verified: number, rejected: number): string {
  if (verified + rejected === 0){
    return 'No report history';
  }
  return `${verified} verified | ${rejected} rejected`;
}

export function RoleApprovalModal({
  request,
  onClose,
  onApprove,
  onReject,
  onRevoke,
}: RoleApprovalModalProps) {
  const isPending = request.status === 'pending';

  return (
    <dialog
      open
      data-testid="approval-modal"
      className="modal modal-open items-start sm:items-center overflow-y-auto py-14 mb-6"
    > 
      <div className="modal-box bg-carbon-side border border-carbon-stroke rounded-lg p-6 max-w-[calc(56vh-3rem)] max-h-[calc(100vh-3rem)] overflow-y-auto sm:my-auto">
        <div className="flex justify-between items-center gap-4 mb-6">
          <h3 className="text-2xl text-text-primary">
            Role request - {request.user.name} {request.user.surname}
          </h3>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="text-text-muted hover:text-text-primary"
          >
            <X size={16} />
          </button>
        </div>

        {/* Info grid */}
        <div className="grid grid-cols-2 gap-x-8 gap-y-6 mb-4">
          <div>
            <p className="text-sm text-text-muted mb-1">
              Full Name
            </p>
            <p className="text-base font-semibold text-text-primary">
              {request.user.name} {request.user.surname}
            </p>
          </div>
          <div>
            <p className="text-sm text-text-muted mb-1">
              Account Created
            </p>
            <p className="text-sm font-semibold text-text-primary">
              {request.created_at
                ? new Date(request.created_at).toLocaleDateString('en-ZA', {
                    day: 'numeric',
                    month: 'short',
                    year: 'numeric',
                  })
                : '—'}
            </p>
          </div>
          <div>
            <p className="text-sm text-text-muted mb-1">
              Email
            </p>
            <p className="text-base font-semibold text-text-primary break-all">{request.user.email ?? '—'}</p>
          </div>
          <div>
            <p className="text-sm text-text-muted mb-1">
              Status
            </p>
            <RoleStatusBadge status={request.status} />
          </div>
          <div className='col-span-2'>
            <p className="text-sm text-text-muted mb-1">
                Trust Score
            </p>
            <div className='flex items-center gap-3'>
              <ScoreBadge score={request.trust_score} />
              <span className="text-base font-semibold text-text-primary">
                {getReportBreakdown(request.reports_verified, request.reports_rejected)}
              </span>
            </div>
          </div>
        </div>

        <div className="border-t border-carbon-stroke my-6" />

        {/* Current role */}
        <div className="grid grid-cols-2 gap-x-8 gap-y-6 mb-6">
          <div>
            <p className="text-sm text-text-muted mb-1">
              Current Role
            </p>
            <p className="text-base font-semibold text-text-primary capitalize">{request.current_role}</p>
          </div>
          <div>
            <p className="text-sm text-text-muted mb-1">
              Requested Role
            </p>
            <p className="text-base font-semibold text-text-primary capitalize">
              {request.requested_role}
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="border-t border-carbon-stroke pt-2 flex justify-end gap-3">
          {request.status === 'pending' && (
            <>
              <button
                type="button"
                data-testid="reject-btn"
                onClick={() => onReject(request.request_id)}
                className="btn btn-sm btn-error text-lg font-semibold rounded-md border-carbon-stroke text-text-primary hover:bg-smoke-hover"
              >
                Reject
              </button>
              <button
                type="submit"
                data-testid="approve-btn"
                onClick={() => onApprove(request.request_id)}
                className="btn btn-sm text-lg font-bold rounded-md bg-primary border-primary text-text-primary hover:bg-primary/90"
              >
                Approve
              </button>
            </>
          )}
          {request.status === 'approved' && (
            <button
              data-testid="revoke-btn"
              onClick={() => onRevoke(request.request_id)}
              className="btn btn-sm btn-error text-lg font-semibold rounded-md border-carbon-stroke text-text-primary hover:bg-smoke-hover"
            >
              Revoke
            </button>
          )}
        </div>
      </div>
      <form method="dialog" className="modal-backdrop">
        <button onClick={onClose}>close</button>
      </form>
    </dialog>
  );
}
