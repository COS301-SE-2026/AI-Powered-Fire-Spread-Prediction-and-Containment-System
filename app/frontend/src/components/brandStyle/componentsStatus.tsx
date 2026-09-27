import { ComponentsGroup, Labled } from './componentsGroup';
import { RoleStatusBadge } from '../admin/RoleStatusBadge';
import { ReportStatusBadge } from '../admin/ReportStatusBadge';

export function StatusBadges() {
  return (
    <>
      <ComponentsGroup title="Report Status Badge">
        <div className="flex flex-wrap items-center gap-22">
          <Labled caption="pending">
            <ReportStatusBadge status="pending" />
          </Labled>
          <Labled caption="verified">
            <ReportStatusBadge status="verified" />
          </Labled>
          <Labled caption="rejected">
            <ReportStatusBadge status="rejected" />
          </Labled>
        </div>
      </ComponentsGroup>

      <ComponentsGroup title="Approval Status Badge">
        <div className="flex flex-wrap items-center gap-9">
          <Labled caption="pending">
            <RoleStatusBadge status="pending" />
          </Labled>
          <Labled caption="approved">
            <RoleStatusBadge status="approved" />
          </Labled>
          <Labled caption="rejected">
            <RoleStatusBadge status="rejected" />
          </Labled>
          <Labled caption="revoked">
            <RoleStatusBadge status="revoked" />
          </Labled>
        </div>
      </ComponentsGroup>
    </>
  );
}

