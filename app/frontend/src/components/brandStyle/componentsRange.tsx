import { ComponentsGroup } from "./componentsGroup"

export function Range() {
    return (
        <ComponentsGroup title="Range Slider">
            <div className="w-90">
                <input type="range" min={0} max="24" step="0.5" defaultValue={12} className="range range-xs w-full" />
                <div className="flex justify-between px-2.5 mt-2 text-sm">
                    <span>0h</span>
                    <span>6h</span>
                    <span>12h</span>
                    <span>18h</span>
                    <span>24h</span>
                </div>
            </div>
        </ComponentsGroup>
    );
}