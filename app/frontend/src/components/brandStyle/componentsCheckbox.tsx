import { ComponentsGroup, Labled } from './componentsGroup';

export function Checkbox() {
  return (
    <ComponentsGroup title="Checkbox States">
      <div className="flex flex-wrap tiems-center gap-24">
        <Labled caption="unchecked">
          <input
            type="checkbox"
            aria-label="Unchecked checkbox example"
            className="checkbox checkbox-sm rounded-lg"
          />
        </Labled>
        <Labled caption="checked">
          <input
            type="checkbox"
            defaultChecked
            aria-label="Checked checkbox example"
            className="checkbox checkbox-sm rounded-lg"
          />
        </Labled>
        <Labled caption="disabled">
          <input
            type="checkbox"
            disabled
            aria-label="Disabled checkbox example"
            className="checkbox checkbox-sm rounded-lg"
          />
        </Labled>
      </div>
    </ComponentsGroup>
  );
}
