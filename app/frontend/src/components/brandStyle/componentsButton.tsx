import { ComponentsGroup, Labled } from "./componentsGroup";

export function ButtonComponents() {
    return (
        <>
        <ComponentsGroup title="Button Varients">
            <button className="btn btn-primary text-xl">Primary</button>
            <button className="btn btn-secondary text-xl">Secondary</button>
            <button className="btn btn-ghost text-xl">Ghost</button>
            <button className="btn btn-outline text-xl">Outline</button>
            <button className="btn btn-error text-xl">Error</button>
        </ComponentsGroup>
        </>
    );
}
