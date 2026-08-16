import { ComponentsGroup, Labled } from './componentsGroup';
import { Alert } from '../shared/Alerts';

export function Alerts() {
  return (
    <ComponentsGroup title="Allert variants">
      <div className="flex flex-col gap-3 w-full max-w-sm">
        <Labled caption="success">
          <Alert variant="success" message="Fire report submitted successfully." />
        </Labled>
        <Labled caption="error">
          <Alert variant="error" message="Please select a valid location." />
        </Labled>
        <Labled caption="warning">
          <Alert variant="warning" message="Location permission not granted." />
        </Labled>
        <Labled caption="info">
          <Alert variant="info" message="Map data last synced 3 min ago." />
        </Labled>
      </div>
    </ComponentsGroup>
  );
}
