"use client";

import React, { useState } from "react";
import dynamic from "next/dynamic";
import { SidebarLayout } from "../components/reportfire/Sidebar";
import StepIndicator from "../components/reportfire/Stepindicator";
import MapKey from "../components/reportfire/Mapkey";
import ReportDetailsForm, { type ReportFormData } from "../components/reportfire/Reportdetailsform";
import ReportStatus from "../components/reportfire/Reportstatus";

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

export default function ReportPage() {
  const [activeStep, setActiveStep]     = useState(0);
  const [location, setLocation]         = useState("Click the map to drop a pin");
  const [boundarySize, setBoundarySize] = useState(2);
  const [statusIndex, setStatusIndex]   = useState(-1);
  const [mapKey, setMapKey]             = useState(0);
  const [activeRefNum, setActiveRefNum] = useState("");
  /** Coords from the form's geocoding search — passed as a prop to FireMap */
  const [externalPin, setExternalPin]   = useState<{ lng: number; lat: number } | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError]   = useState<string | null>(null);
  const [pinCoords, setPinCoords]       = useState<{ lat: number; lng: number } | null>(null);


  function handleBoundarySizeChange(value: number) {
    setBoundarySize(value);
    if (activeStep < 1) setActiveStep(1);
  }

  function handleLocationSelect(loc: { lat: number; lng: number; address: string }) {
    setLocation(loc.address);
    setPinCoords({ lat: loc.lat, lng: loc.lng });
    setActiveStep((prev) => Math.max(prev, 1));
  }

  /** Called when user picks an address from the form's autocomplete */
  function handleLocationSearch(loc: { lat: number; lng: number; address: string }) {
    setLocation(loc.address);
    setPinCoords({ lat: loc.lat, lng: loc.lng });
    setActiveStep((prev) => Math.max(prev, 1));
    setExternalPin({ lng: loc.lng, lat: loc.lat });
  }

  async function handleSubmit(data: ReportFormData) {
    if (!pinCoords) return;

    setIsSubmitting(true);
    setSubmitError(null);

    try {
        const res = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/fire-reports/`,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    location_text:      data.location,
                    description:        data.description ?? "",
                    location_geom:      `SRID=4326;POINT(${pinCoords.lng} ${pinCoords.lat})`,
                    boundary_radius_km: boundarySize,
                }),
            }
        );

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err?.detail ?? "Submission failed");
        }

        const report = await res.json();

        setActiveRefNum(report.reference_number);
        setStatusIndex(report.status_index);
        setActiveStep(2);

        setTimeout(() => {
            setActiveStep(0);
            setLocation("Click the map to drop a pin");
            setBoundarySize(2);
            setExternalPin(null);
            setPinCoords(null);
            setMapKey((k) => k + 1);
        }, 1000);

    } catch (err) {
        setSubmitError(err instanceof Error ? err.message : "Submission failed");
    } finally {
        setIsSubmitting(false);
    }
  }

  return (
    <SidebarLayout>
      <div className="flex flex-col p-6">
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

        <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 xl:grid-rows-1">

          {/* Left Column */}
          <div className="xl:col-span-8 flex flex-col gap-4">
            <div className="rounded-2xl bg-carbon-side/40 border border-carbon-stroke backdrop-blur-sm flex flex-col overflow-hidden relative shadow-2xl shadow-black/20 h-[480px]">
              <div className="p-4 border-b border-carbon-card bg-carbon-bg/50 backdrop-blur-md absolute top-0 w-full z-10 flex justify-between items-center border-l-2 border-l-ignite/60">
                <span className="font-bold text-m tracking-wide text-neutral/80 uppercase font-display">
                  Live Incident Map Context
                </span>
              </div>
              <div className="flex-1 w-full h-full pt-[53px]">
                <FireMap
                  key={mapKey}
                  externalPin={externalPin}
                  onLocationSelect={handleLocationSelect}
                  onBoundarySizeChange={handleBoundarySizeChange}
                />
              </div>
            </div>

            <div className="flex flex-col">
              <h2 className="text-xs font-bold tracking-widest text-neutral/50 uppercase mb-3">
                Map Legend Variables
              </h2>
              <div className="rounded-2xl bg-carbon-side/40 border border-carbon-stroke backdrop-blur-sm p-4 shadow-xl">
                <MapKey />
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="xl:col-span-4 flex flex-col gap-3" style={{ maxHeight: '100%' }}>
            <h2 className="text-xs font-bold tracking-widest text-neutral/50 uppercase shrink-0">
              Operational Parameters
            </h2>
            <div
              className="rounded-2xl bg-carbon-side/40 backdrop-blur-md border border-carbon-card p-5 shadow-2xl flex flex-col gap-5 overflow-y-auto"
              style={{ maxHeight: 'calc(480px + 1rem + 155px)' }}
            >
              <ReportDetailsForm
                location={location}
                onSubmit={handleSubmit}
                onLocationSearch={handleLocationSearch}
                isSubmitting={isSubmitting}
                submitError={submitError}
            />
              <div className="border-t border-white/5 pt-4">
                <ReportStatus activeIndex={statusIndex} currentRef={activeRefNum} />
              </div>
            </div>
          </div>

        </div>
      </div>
    </SidebarLayout>
  );
}