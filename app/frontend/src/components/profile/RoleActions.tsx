import type { UserResponse, UserRole } from "../../types/User";
import type { RoleRequest } from '../../types/RoleRequest';

interface RoleActionProps {
    userRole: UserRole;
    user: UserResponse;
    pending: RoleRequest | undefined;
    loading: boolean;
    busy: boolean;
    run: (action: () => Promise<void>) => void;
    requestRole: (payload: { requested_role: UserRole }) => Promise<void>;
    cancelRequest: () => Promise<void>;
}

 export function RoleActions({ userRole, user, pending, loading, busy, run, requestRole, cancelRequest }: RoleActionProps){
    if (user.role === userRole){
        return <span className='uppercase text-success font-bold text-sm'>Current</span>;
    }
    const isPending = pending?.requested_role === userRole;

    return (
        <button type="button" className='text-xs font-semibold btn btn-sm btn-outline border rounded-xl text-text-primary hover:bg-smoke-hover hover:text-text-primary transition-colors' disabled={loading || busy || (!isPending && pending !== undefined)} onClick={() => run(isPending ? cancelRequest : () => requestRole({ requested_role: userRole }))}>
            {isPending ? 'Cancel request' : 'Request'}
        </button>
    );
}