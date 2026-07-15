"use client";

import React, { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import StepIndicator from "./Stepindicator";
import MapKey from "./Mapkey";
import ReportDetailsForm, { type ReportFormData } from "./Reportdetailsform";
import ReportStatus from "./Reportstatus";

const FireMap = dynamic(
  () => import("./Firemap").then((mod) => mod.FireMap),
  {
    ssr: false,
    loading: () => (
      <div className="flex-1 flex items-center justify-center bg-carbon-side/20 animate-pulse h-full w-full">
        <span className="text-neutral/40 font-display tracking-widest text-sm uppercase">
          Loading...
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

type SubmitState = "idle" | "loading" | "error";

export default function ReportPage() {
  const [activeStep, setActiveStep]     = useState(0);
  const [location, setLocation]         = useState("Click the map to drop a pin");
  const [boundarySize, setBoundarySize] = useState(200);
  const [statusIndex, setStatusIndex]   = useState(-1);
  const [mapKey, setMapKey]             = useState(0);
  const [activeRefNum, setActiveRefNum] = useState("");
  const [externalPin, setExternalPin]   = useState<{ lng: number; lat: number } | null>(null);
  const [fireReports, setFireReports]   = useState<any[]>([]);
  const [submitState, setSubmitState]   = useState<SubmitState>("idle");
  const [submitError, setSubmitError]   = useState<string | null>(null);

  useEffect(() => {
    fetch(`/api/users/reported-fires`)
      .then(res => res.json())
      .then(data => setFireReports(data))
      .catch(err => console.error('Failed to fetch reports', err));
  }, []);

  function handleBoundarySizeChange(value: number) {
    setBoundarySize(value);
    if (activeStep < 1) setActiveStep(1);
  }

  function handleLocationSelect(loc: { lat: number; lng: number; address: string }) {
    setLocation(loc.address);
    setExternalPin({ lng: loc.lng, lat: loc.lat });
    setActiveStep((prev) => Math.max(prev, 1));
  }

  function handleLocationSearch(loc: { lat: number; lng: number; address: string }) {
    setLocation(loc.address);
    setActiveStep((prev) => Math.max(prev, 1));
    setExternalPin({ lng: loc.lng, lat: loc.lat });
  }

  async function handleSubmit(data: ReportFormData) {
    setSubmitState("loading");
    setSubmitError(null);
    try {
      let imageUrl = "";

      if (data.photo){  // upload image first if one was attatched
        const formData = new FormData();
        formData.append("file", data.photo);

        const uploadRes = await fetch(`/api/uploads/photo`, {
          method: "POST",
          body: formData,
        });

        if (!uploadRes.ok){
          throw new Error("Image upload failed");
        }

        const uploadResult = await uploadRes.json();
        imageUrl = uploadResult.object_key;
      }

      const res = await fetch(`/api/users/reported-fires`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          location_text: data.location,
          description: data.description,
          image_url: "pending-url",
          lat: externalPin?.lat ?? 0,
          lng: externalPin?.lng ?? 0,
          boundary_radius: boundarySize,
        }),
      });
      const report = await res.json();
      setActiveRefNum(report.reference_number);
      setStatusIndex(0);
      setActiveStep(2);
      setSubmitState("idle");
      setTimeout(() => {
        setActiveStep(0);
        setLocation('Click the map to drop a pin');
        setBoundarySize(2);
        setExternalPin(null);
        setMapKey((k) => k + 1);
      }, 1000);
    } catch (err) {
      console.error('Failed to submit report', err);
      setSubmitState("error");
      setSubmitError("Failed to submit report. Please try again.");
    }
  }

  return (
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
                  Live Map
                </span>
              </div>
              <div className="flex-1 w-full h-full pt-[53px]">
                <FireMap
                  key={mapKey}
                  externalPin={externalPin}
                  onLocationSelect={handleLocationSelect}
                  onBoundarySizeChange={handleBoundarySizeChange}
                  fireReports={fireReports}
                />
              </div>
            </div>

            <div className="flex flex-col">
              <h2 className="text-xs font-bold tracking-widest text-neutral/50 uppercase mb-3">
                Map Legend
              </h2>
              <div className="rounded-2xl bg-carbon-side/40 border border-carbon-stroke backdrop-blur-sm p-4 shadow-xl">
                <MapKey />
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="xl:col-span-4 flex flex-col gap-3" style={{ maxHeight: '100%' }}>
            <div
              className="rounded-2xl bg-carbon-side/40 backdrop-blur-md border border-carbon-card p-5 shadow-2xl flex flex-col gap-5 overflow-y-auto"
              style={{ maxHeight: 'calc(480px + 1rem + 155px)' }}
            >
              <ReportDetailsForm
                location={location}
                onSubmit={handleSubmit}
                onLocationSearch={handleLocationSearch}
              />
              <div className="border-t border-white/5 pt-4">
                <ReportStatus activeIndex={statusIndex} currentRef={activeRefNum} />
              </div>
            </div>
          </div>

        </div>
      </div>
  );
}