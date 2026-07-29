import { ComponentsGroup, Labled } from "./componentsGroup";
import { Pencil, CirclePlay } from "lucide-react";

export function ButtonComponents() {
    return (
        <>
            <ComponentsGroup title="Button Varients">
                <div className ="flex flex-wrap justify-start items-center gap-8">
                    <button className="btn btn-primary text-lg">Primary</button>
                    {/* <button className="btn btn-secondary text-lg">Secondary</button> */}
                    <button className="btn btn-ghost text-lg">Ghost</button>
                    <button className="btn btn-outline text-lg">Outline</button>
                    {/* <button className="btn btn-error text-lg">Error</button> */}
                    {/* <button className="btn btn-accent text-lg">Accent</button> */}
                    <button className="btn btn-neutral text-lg">Neutral</button>
                    {/* <button className="btn btn-info text-lg">Info</button> */}
                    <button className="btn btn-success text-lg">Success</button>
                    {/* <button className="btn btn-warning text-lg">Warning</button> */}
                    <button className="btn btn-link text-lg">Link</button>
                    {/* <button className="btn btn-soft text-lg">Soft</button> */}
                    <button className="btn btn-dash text-lg">Dash</button>
                </div>
            </ComponentsGroup>

            <ComponentsGroup title="Button Sizes">
                <div className ="flex flex-wrap justify-start items-center gap-27">
                    <button className="btn btn-primary btn-sm w-24 text-m">sm</button>
                    <button className="btn btn-primary btn-md w-28 text-lg">m</button>
                    <button className="btn btn-primary btn-lg w-32 text-xl">lg</button>
                    <button className="btn btn-primary btn-xl w-36 text-xl">xl</button>
                </div>
            </ComponentsGroup>

            <ComponentsGroup title="Button States">
                <div className ="flex flex-wrap items-center gap-11">
                    <Labled caption="default">
                        <button className="btn btn-primary text-lg">Report Fire</button>
                    </Labled>
                    <Labled caption="hover (forced)">
                        <button className="btn btn-ghost text-lg hover:bg-primary-focus hover:scale-105">
                            Report Fire
                        </button>
                    </Labled>
                    <Labled caption="focus (forced)">
                        <button className="btn btn-primary text-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-carbon-card focus:ring-primary">
                            Report Fire
                        </button>
                    </Labled>
                    <Labled caption="active (forced)">
                        <button className="btn btn-primary text-lg active:scale-90">
                            Register
                        </button>
                    </Labled>
                    <Labled caption="disabled">
                        <button className="btn btn-primary  text-lg" disabled>Report Fire</button>
                    </Labled>
                    <Labled caption="error">
                        <button className="btn btn-error  text-lg">Failed</button>
                    </Labled>
                    <Labled caption="loading ">
                        <button className="btn btn-primary">
                            <span className="loading loading-spinner loading-sm"/>
                            Submitting
                        </button>
                    </Labled>
                    <Labled caption="Firefighter draw containment line">
                        <button className="btn btn-primary rounded-lg btn-outline btn-wide btn-xl p-2">
                            <Pencil size={28} />
                            Draw Containment
                        </button>
                    </Labled>
                    <Labled caption="Firefighter RUN simulation">
                        <button className="btn btn-primary rounded-lg btn-outline btn-wide btn-xl p-2">
                            <CirclePlay />
                            RUN
                        </button>
                    </Labled>
                </div>
            </ComponentsGroup>

        </>
    );
}
