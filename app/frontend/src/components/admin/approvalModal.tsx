import { RoleRequest } from "../../types/admin";

interface RoleApprovalModalProps {
    request: RoleRequest;
    onClose: () => void;
    onApprove: (id:string) => void;
    onReject: (id:string) => void;
}

export function RoleApprovalModal({ request, onClose, onApprove, onReject }: RoleApprovalModalProps) {
    return (
        <dialog open className="modal modal-open">
            <div className="modal-box bg-carbon-side border border-carbon-card">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="font-bold text-lg">Role request - {request.user_id}</h3>
                    <button onClick={onClose} className="text-neutral/50 hover:text-neutral">✕</button>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                        <p className="text-xs text-neutral/50 uppercase tracking-widest mb-1">User ID</p>
                        <p className="text-sm text-neutral">{request.user_id}</p>
                    </div>

                    <div>
                        <p className="text-xs text-neutral/50 uppercase tracking-widest mb-1">Current Role</p>
                        <p className="text-sm text-neutral">Guest</p>
                    </div>

                    <div>
                        <p className="text-xs text-neutral/50 uppercase tracking-widest mb-1">Requested Role</p>
                        <p className="text-sm text-neutral">{request.role}</p>
                    </div>

                    <div>
                        <p className="text-xs text-neutral/50 uppercase tracking-widest mb-1">status</p>
                        <p className="text-sm text-neutral">{request.status}</p>
                    </div>
                </div>

                <div className="border-t border-carbon-card pt-4 flex justify-end gap-2">
                    {request.status === 'pending' ? (
                        <>
                            <button onClick={() => onReject(request.request_id)} className="btn btn-error btn-sm">Reject</button>
                            <button onClick={() => onApprove(request.request_id)} className="btn btn-success btn-sm">Approve</button>
                        </>
                    ): (
                        <button className="text-xs font-semibold px-4 py-2 rounded-lg border border-carbon-card text-neutral/50 hover:bg-smoke-hover">Revoke</button>
                    )}
                </div>
            </div>

            <form method="dialog" className="modal-backdrop">
                    <button onClick={onClose}>close</button>
                </form>
        </dialog>
    );
}