import { useState } from "react";
import StepIndicator from "../components/reportfire/Stepindicator";
import FireMap from "../components/reportfire/Firemap";
import MapKey from "../components/reportfire/Mapkey";
import ReportDetailsForm, { type ReportFormData } from "../components/reportfire/Reportdetailsform";
import ReportStatus from "../components/reportfire/Reportstatus";

const STEPS = [
  { label: "Drop a pin on the map" },
  { label: "Drag boundary ring to show size" },
  { label: "Add details and submit" },
];

export default function ReportPage() {
  const [activeStep, setActiveStep]     = useState(0);
  const [location]                      = useState("Albertskroon, JHB");
  const [boundarySize, setBoundarySize] = useState(2);
  const [statusIndex, setStatusIndex]   = useState(-1); // -1 = nothing selected on load

  function handleBoundarySizeChange(value: number) {
    setBoundarySize(value);
    if (activeStep < 1) setActiveStep(1);
  }

  function handleSubmit(data: ReportFormData) {
    console.log("Fire report submitted:", data);
    setStatusIndex(0); // advance to first status step on submit
    setActiveStep(2);
  }

  return (
    <div className="min-h-screen bg-carbon-bg text-[#EDEAE5] font-body flex flex-col select-none">

      {/* Header */}
      <header className="px-8 pt-8 pb-4">
        <h1 className="text-3xl font-display font-black tracking-wider uppercase text-white mb-3">
          Report a fire
        </h1>
        <StepIndicator steps={STEPS} />
      </header>

      {/* Main layout */}
      <main className="flex-1 grid grid-cols-1 xl:grid-cols-4 px-8 pb-8 gap-6 min-h-0">

        {/* Map (3 cols) */}
        <section className="xl:col-span-3 flex flex-col gap-3 min-h-0">
          { <div className="flex-1 rounded-md overflow-hidden border border-white/5 shadow-2xl">
           // <FireMap location={location} />
          </div> }
          <div className="border border-white/5 rounded-md p-3">
            <MapKey />
          </div>
        </section>

        {/* Sidebar (1 col) */}
        <aside className="bg-carbon-side border border-white/5 rounded-md flex flex-col overflow-hidden shadow-2xl">
          <div className="flex-1 overflow-y-auto p-5 flex flex-col gap-6">

            <ReportDetailsForm
              location={location}
              boundarySize={boundarySize}
              onBoundarySizeChange={handleBoundarySizeChange}
              onSubmit={handleSubmit}
            />

            <ReportStatus activeIndex={statusIndex} />
          </div>
        </aside>

      </main>
    </div>
  );
}