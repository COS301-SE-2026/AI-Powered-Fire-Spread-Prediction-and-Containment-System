import { RoleRequest } from "../../types/admin";
import { statusBadge } from './statusBadge';

interface RoleApprovalModalProps {
    request: RoleRequest;
    onClose: () => void;
    onApprove: (id:string) => void;
    onReject: (id:string) => void;
    onRevoke: (id:string) => void;
}

export function RoleApprovalModal({ request, onClose, onApprove, onReject, onRevoke }: RoleApprovalModalProps) {
    const isPending = request.status === 'pending';

    return (
        <dialog open className="modal modal-open backdrop-blur-sm bg-black/40">
            <div className="modal-box bg-gradient-to-br from-carbon-side to-carbon-bg border border-ignite/60 border-l-4 border-l-ignite rounded-2xl shadow-2xl shadow-ignite/5 max-w-md p-8">

                {/* Header */}
                <div className="flex justify-between items-center mb-6 pb-4 border-b border-ignite/30">
                    <h3 className="font-display font-bold text-xl tracking-wider text-neutral uppercase">Role request - {request.user_full_name}</h3>
                    <button onClick={onClose} className="text-neutral/40 hover:text-neutral transition-colors">✕</button>
                </div>

                {/* Info grid */}
                <div className="grid grid-cols-2 gap-x-6 gap-y-4 mb-6">
                    <div>
                        <p className="text-xs font-bold tracking-widest text-neutral/40 uppercase mb-1">Full Name</p>
                        <p className="text-sm font-semibold text-neutral">{request.user_full_name}</p>
                    </div>
                    <div>
                        <p className="text-xs font-bold tracking-widest text-neutral/40 uppercase mb-1">Account Created</p>
                        <p className="text-sm font-semibold text-neutral">{request.created_at ? new Date(request.created_at).toLocaleDateString('en-ZA', { day: 'numeric', month: 'short', year: 'numeric' }): '—'}</p>
                    </div>
                    <div>
                        <p className="text-xs font-bold tracking-widest text-neutral/40 uppercase mb-1">Email</p>
                        <p className="text-sm font-semibold text-neutral">{request.email ?? '—'}</p>
                    </div>
                    <div>
                    <p className="text-xs font-bold tracking-widest text-neutral/40 uppercase mb-1">Status</p>
                    {(() => {
                        const badge = statusBadge[request.status] ?? {};
                        return (
                            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border capitalize ${badge.bg ?? 'bg-carbon-card'} ${badge.text ?? 'text-neutral/50'} ${badge.border ?? 'border-carbon-card'}`}>
                                {request.status}
                            </span>
                        );
                        })()}
                    </div>
                </div>

                <div className="border-t border-ignite/30 my-4" />

                {/* Current role */}
                <div className="grid grid-cols-2 gap-x-6 gap-y-4 mb-6">
                    <div>
                        <p className="text-xs font-bold tracking-widest text-neutral/40 uppercase mb-1">Current Role</p>
                        <p className="text-sm font-semibold text-neutral">{request.role}</p>
                    </div>
                    {isPending && (
                        <div>
                            <p className="text-xs font-bold tracking-widest text-neutral/40 uppercase mb-1">Requested Role</p>
                            <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-torch/20 text-torch border border-torch/30">
                                {request.role}
                            </span>
                        </div>
                    )}
                </div>

                {/* Actions */}
                <div className="border-t border-ignite/30 pt-4 flex justify-end gap-2">
                    {isPending ? (
                        <>
                            <button onClick={() => onReject(request.request_id)} className="text-xs font-semibold px-4 py-2 rounded-lg border border-ignite/30 text-flare hover:bg-ignite/10 transition-colors">
                                Reject
                            </button>
                            <button onClick={() => onApprove(request.request_id)} className="text-xs font-semibold px-4 py-2 rounded-lg bg-humidity/20 text-humidity border border-humidity/30 hover:bg-humidity/30 transition-colors">
                                Approve
                            </button>
                        </>
                    ) : (
                        <button onClick={() => onRevoke(request.request_id)} className="text-xs font-semibold px-4 py-2 rounded-lg border border-ignite/30 text-flare hover:bg-ignite/10 transition-colors">
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