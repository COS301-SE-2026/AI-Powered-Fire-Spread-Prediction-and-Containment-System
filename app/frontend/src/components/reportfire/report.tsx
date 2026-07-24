"use client";

import React, { useState, useEffect } from "react";
import StepIndicator from "./Stepindicator";
import ReportDetailsForm, { type ReportFormData } from "./Reportdetailsform";
import ReportStatus from "./Reportstatus";
import { FireMap } from "../DynamicUserMap"
import { FormError } from "./ReportFormError";
import { LOCATION_PLACEHOLDER } from "./Reportdetailsform";
import type { FireReport } from "../../types/report";

type SubmitState = "idle" | "loading" | "error";

export default function ReportPage() {
  const [activeStep, setActiveStep] = useState(0);
  const [location, setLocation] = useState(LOCATION_PLACEHOLDER);
  const [boundarySize, setBoundarySize] = useState(0.2);
  const [statusIndex, setStatusIndex] = useState(-1);
  const [mapKey, setMapKey] = useState(0);
  const [activeRefNum, setActiveRefNum] = useState("");
  const [externalPin, setExternalPin] = useState<{ lng: number; lat: number } | null>(null);
  const [submitState, setSubmitState] = useState<SubmitState>("idle");
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [reports, setReports] = useState<FireReport[]>([]);

  useEffect(() => {
    fetch(`/api/users/reported-fires`)
        .then((res) => res.json())
        .then((data: FireReport[]) => {
            const sorted = [...data].sort(
                (a, b) => new Date(b.submitted_at).getTime() - new Date(a.submitted_at).getTime()
            );
            setReports(sorted);
        })
        .catch((err) => console.error("Failed to fetch reports", err));
  }, [activeRefNum]);

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
          image_url: imageUrl,
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
        setLocation(LOCATION_PLACEHOLDER);
        setBoundarySize(0.2);
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
      <div className="flex flex-col p-2">
        <header className="mb-4">
            <h1 className="uppercase">Report a fire</h1>
            <div className="mt-2">
              <StepIndicator />
            </div>
        </header>

        <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 xl:grid-rows-1">

          {/* Left Column */}
          <div className="xl:col-span-8 flex flex-col gap-4">
            <div className="rounded-lg bg-carbon-side border border-carbon-stroke flex flex-col overflow-hidden h-150">
              <div className="p-4 border-b border-carbon-card">
                <span className="font-display font-bold tracking-wide uppercase text-lg">
                  Live Map
                </span>
              </div>
              <div className="flex-1 w-full">
                <FireMap
                  key={mapKey}
                  externalPin={externalPin}
                  onLocationSelect={handleLocationSelect}
                  onBoundarySizeChange={handleBoundarySizeChange}
                />
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="xl:col-span-4 flex flex-col gap-3">
            <div className="rounded-lg bg-carbon-side border border-carbon-stroke p-3 overflow-y-auto">
              <ReportDetailsForm
                location={location}
                onSubmit={handleSubmit}
                onLocationSearch={handleLocationSearch}
              />
            </div>

            <div className="rounded-lg bg-carbon-side border border-carbon-stroke p-3 overflow-y-auto">
              <h4 className = "mb-2">Report status</h4>
              {submitState === "error" && submitError && <FormError message={submitError} />}
              
              {reports.length == 0 ? (
                <p className="text-sm text-neutural">No reports submitted yet.</p>
              ) : (
                <div className="flex flex-col gap-3 max-h-15 overflow-y-auto">
                {reports.map((report) => (
                    <ReportStatus
                        key={report.id}
                        status={report.status}
                        refNumber={report.reference_number}
                        locationText={report.location_text}
                    />
                ))}
              </div>
              )}
            </div>
          </div>

        </div>
      </div>
  );
}