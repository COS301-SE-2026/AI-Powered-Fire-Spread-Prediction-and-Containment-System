import { ComponentsGroup, Labled } from "./componentsGroup";
import { StatusBadge } from "../admin/reportStatusBadge";
import { statusBadge, BadgeStyle } from "../admin/statusBadge";
import type { RoleStatus } from "../../types/RoleRequest";

function RoleBadge({ status }: RoleBadgeProps) {
    const { bg = 'bg-carbon-card', text = 'text-text-primary/50', border = '' }: BadgeStyle = statusBadge[status] ?? {};

    return (
        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border capitalize ${bg} ${text} ${border}`}>
            {status}
        </span>
    );
}

export function StatusBadges() {
  return <>
            <ComponentsGroup title="Report Status Badge">
                <div className="flex flex-wrap items-center gap-22">
                    <Labled caption="pending"><StatusBadge status="pending" /></Labled>
                    <Labled caption="verified"><StatusBadge status="verified" /></Labled>
                    <Labled caption="rejected"><StatusBadge status="rejected" /></Labled>
                </div>
            </ComponentsGroup>

            <ComponentsGroup title="Approval Status Badge">
                <div className="flex flex-wrap items-center gap-9">
                    <Labled caption="pending"><RoleBadge status="pending" /></Labled>
                    <Labled caption="approved"><RoleBadge status="approved" /></Labled>
                    <Labled caption="rejected"><RoleBadge status="rejected" /></Labled>
                    <Labled caption="revoked"><RoleBadge status="revoked" /></Labled>
                </div>
            </ComponentsGroup>
        </>
}
type RoleBadgeProps = Readonly<{ status: RoleStatus }>;

