"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import { SidebarLayout } from "../components/reportfire/Sidebar";
import StepIndicator from "../components/reportfire/Stepindicator";
import MapKey from "../components/reportfire/Mapkey";
import ReportDetailsForm, { type ReportFormData } from "../components/reportfire/Reportdetailsform";
import ReportStatus from "../components/reportfire/Reportstatus";
import 'mapbox-gl/dist/mapbox-gl.css';

// ── DYNAMIC MAP ENCAPSULATION PIPELINE ────────────────────────
const FireMap = dynamic(
  () => import("../components/reportfire/Firemap").then((mod) => mod.FireMap),
  {
    ssr: false,
    loading: () => (
      <div className="flex-1 flex items-center justify-center bg-carbon-side/20 animate-pulse h-full w-full">
        <span className="text-neutral/40 font-display tracking-widest text-sm uppercase">
          Initializing Map Layer
        </span>
      </div>
    ),
  }
);

const STEPS = [
  { label: "Drop a pin on the map" },
  { label: "Drag boundary ring to show size" },
  { label: "Add details and submit" },
];

// ── All state lives here so re-renders never touch SidebarLayout ──
function ReportContent() {
  const [activeStep, setActiveStep]     = useState(0);
  const [location, setLocation]         = useState("Click the map to drop a pin");
  const [boundarySize, setBoundarySize] = useState(2);
  const [statusIndex, setStatusIndex]   = useState(-1);
  const [mapKey, setMapKey]             = useState(0); // ← incrementing this remounts the map

  function handleBoundarySizeChange(value: number) {
    setBoundarySize(value);
    if (activeStep < 1) setActiveStep(1);
  }

  function handleLocationSelect(loc: { lat: number; lng: number; address: string }) {
    setLocation(loc.address);
    setActiveStep((prev) => Math.max(prev, 1));
  }

  function handleSubmit(data: ReportFormData) {
    console.log("Fire report submitted:", data);
    setStatusIndex(0);
    setActiveStep(2);

    // Reset everything back to initial state after a short delay so the
    // user can see the success status before it clears
    setTimeout(() => {
      setActiveStep(0);
      setLocation("Click the map to drop a pin");
      setBoundarySize(2);
      setMapKey((k) => k + 1); // ← remounts FireMap, resetting pin + boundary ring
    }, 2000);
  }

  return (
    <div className="flex flex-col p-6 text-[#EDEAE5] font-body select-none">

      {/* ── HEADER MODULE SECTION ── */}
      <header className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold tracking-wider text-neutral uppercase">
            Report a fire
          </h1>
          <div className="mt-2">
            <StepIndicator steps={STEPS} />
          </div>
        </div>
      </header>

      {/* ── MAIN DASHBOARD GRID CONTAINER ── */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 xl:grid-rows-1">

        {/* Left Column: Spatial Mapping & Legend Parameters (8 Cols) */}
        <div className="xl:col-span-8 flex flex-col gap-4">

          {/* Map Frame Card Container */}
          <div className="rounded-2xl bg-carbon-side/40 border border-carbon-stroke backdrop-blur-sm flex flex-col overflow-hidden relative shadow-2xl shadow-black/20 h-[480px] isolate">

            {/* Contextual Header Overlay Plate */}
            <div className="p-4 border-b border-carbon-card bg-carbon-bg/50 backdrop-blur-md absolute top-0 w-full z-10 flex justify-between items-center border-l-2 border-l-ignite/60">
              <span className="font-bold text-m tracking-wide text-neutral/80 uppercase font-display">
                Live Incident Map Context
              </span>
            </div>

            {/* Active Map Spatial Window */}
            <div className="flex-1 w-full h-full pt-[53px] relative">
              <FireMap
                key={mapKey}
                onLocationSelect={handleLocationSelect}
                onBoundarySizeChange={handleBoundarySizeChange}
              />
            </div>

          </div> {/* ← end Map Frame Card */}

          {/* Map Legend Frame */}
          <div className="flex flex-col">
            <h2 className="text-xs font-bold tracking-widest text-neutral/50 uppercase mb-3">
              Map Legend Variables
            </h2>
            <div className="rounded-2xl bg-carbon-side/40 border border-carbon-stroke backdrop-blur-sm p-4 shadow-xl">
              <MapKey />
            </div>
          </div>

        </div> {/* ← end Left Column */}

        {/* Right Column: Incident Form & Action Steppers (4 Cols) */}
        <div className="xl:col-span-4 flex flex-col gap-3" style={{ maxHeight: '100%' }}>

          <h2 className="text-xs font-bold tracking-widest text-neutral/50 uppercase shrink-0">
            Operational Parameters
          </h2>

          {/* Input Form Parameters Card Block */}
          <div
            className="rounded-2xl bg-carbon-side/40 backdrop-blur-md border border-carbon-card p-5 shadow-2xl flex flex-col gap-5 overflow-y-auto"
            style={{ maxHeight: 'calc(480px + 1rem + 155px)' }}
          >
            <ReportDetailsForm
              location={location}
              onSubmit={handleSubmit}
            />

            {/* Broadcast Status Node Component */}
            <div className="border-t border-white/5 pt-4">
              <ReportStatus activeIndex={statusIndex} />
            </div>
          </div>

        </div> {/* ← end Right Column */}

      </div> {/* ← end Grid */}
    </div>
  );
}

// ── SidebarLayout never re-renders — sidebar hover always works ──
export default function ReportPage() {
  return (
    <SidebarLayout>
      <ReportContent />
    </SidebarLayout>
  );
}