import { Pencil, CirclePlay, Flame, LocateFixed } from 'lucide-react';
import { ComponentsGroup, Labled } from './componentsGroup';

export function ButtonComponents() {
  return (
    <>
      <ComponentsGroup title="Button Varients">
        <div className="flex flex-wrap justify-start items-center gap-8">
          <button type="button" className="btn btn-primary text-lg">
            Primary
          </button>
          <button type="button" className="btn btn-ghost text-lg">
            Ghost
          </button>
          <button type="button" className="btn btn-outline text-lg">
            Outline
          </button>
          <button type="button" className="btn btn-neutral text-lg">
            Neutral
          </button>
          <button type="button" className="btn btn-success text-lg">
            Success
          </button>
          <button type="button" className="btn btn-link text-lg">
            Link
          </button>
          <button type="button" className="btn btn-dash text-lg">
            Dash
          </button>
        </div>
      </ComponentsGroup>

      <ComponentsGroup title="Button Sizes">
        <div className="flex flex-wrap justify-start items-center gap-27">
          <button type="button" className="btn btn-primary btn-sm w-24 text-m">
            sm
          </button>
          <button type="button" className="btn btn-primary btn-md w-28 text-lg">
            m
          </button>
          <button type="button" className="btn btn-primary btn-lg w-32 text-xl">
            lg
          </button>
          <button type="button" className="btn btn-primary btn-xl w-36 text-xl">
            xl
          </button>
        </div>
      </ComponentsGroup>

      <ComponentsGroup title="Button States">
        <div className="flex flex-wrap items-center gap-6">
          <Labled caption="default">
            <button type="button" className="btn btn-primary text-lg">
              Report Fire
            </button>
          </Labled>
          <Labled caption="hover (forced)">
            <button
              type="button"
              className="btn btn-ghost text-lg hover:bg-primary-focus hover:scale-105"
            >
              Report Fire
            </button>
          </Labled>
          <Labled caption="focus (forced)">
            <button
              type="button"
              className="btn btn-primary text-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-carbon-card focus:ring-primary"
            >
              Report Fire
            </button>
          </Labled>
          <Labled caption="active (forced)">
            <button type="button" className="btn btn-primary text-lg active:scale-90">
              Register
            </button>
          </Labled>
          <Labled caption="disabled">
            <button type="button" className="btn btn-primary  text-lg" disabled>
              Report Fire
            </button>
          </Labled>
          <Labled caption="error">
            <button type="button" className="btn btn-error  text-lg">
              Failed
            </button>
          </Labled>
          <Labled caption="loading ">
            <button type="button" className="btn btn-primary">
              <span className="loading loading-spinner loading-sm" />
              Submitting
            </button>
          </Labled>
          <Labled caption="Draw containment line">
            <button
              type="button"
              className="btn btn-primary rounded-lg btn-outline btn-wide btn-m p-2"
            >
              <Pencil size={28} />
              Draw Containment
            </button>
          </Labled>
          <Labled caption="RUN simulation">
            <button
              type="button"
              className="btn btn-primary rounded-lg btn-outline btn-wide btn-m p-2"
            >
              <CirclePlay />
              RUN
            </button>
          </Labled>
          <Labled caption="Report fire">
            <button type="button" className="btn btn-ghost gap-2 w-32 text-sm">
              <Flame className="size-5" />
              Report Fire
            </button>
          </Labled>
          <Labled caption="Recenter">
            <button type="button" className="btn btn-ghost gap-2 w-32 text-sm">
              <LocateFixed className="size-5" />
              Report Fire
            </button>
          </Labled>
        </div>
      </ComponentsGroup>
    </>
  );
}
