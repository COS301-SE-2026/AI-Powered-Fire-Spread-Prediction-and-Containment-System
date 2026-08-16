import { ComponentsGroup, Labled } from './componentsGroup';
import ReportStatus from '../reportfire/ReportStatus';

export function StatusCard() {
  return (
    <ComponentsGroup title="Report Status Card">
      <div className="flex flex-col gap-3 w-80">
        <Labled caption="received">
          <ReportStatus status="received" refNumber="FR-1042" locationText="Moreleta Park" />
        </Labled>
        <Labled caption="pending">
          <ReportStatus status="pending" refNumber="FR-1043" locationText="Faerie Glen" />
        </Labled>
        <Labled caption="verified">
          <ReportStatus status="verified" refNumber="FR-1044" locationText="Silver Lakes" />
        </Labled>
        <Labled caption="rejected">
          <ReportStatus status="rejected" refNumber="FR-1045" locationText="Wapadrand" />
        </Labled>
      </div>
    </ComponentsGroup>
  );
}
