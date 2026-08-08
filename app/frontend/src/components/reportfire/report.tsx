"use client";

import React, { useState, useEffect, useReducer, useRef } from "react";
import StepIndicator from "./Stepindicator";
import ReportDetailsForm, { type ReportFormData } from "./Reportdetailsform";
import ReportStatus from "./Reportstatus";
import { FireMap } from "../shared/DynamicUserMap"
import { Alert } from "../shared/Alerts";
import { LOCATION_PLACEHOLDER } from "./Reportdetailsform";
import type { FireReportMapResponse } from "../../types/Report";

type SubmitState = "idle" | "loading" | "error";

interface FormStateProps {
  activeStep: number;
  location: string;
  boundarySize: number;
  externalPin: { lng: number; lat: number } | null;
  mapKey: number;
  submitState: SubmitState;
  submitError: string | null;
}

const initialFormState: FormStateProps = {
  activeStep: 0,
  location: LOCATION_PLACEHOLDER,
  boundarySize: 0.2,
  externalPin: null,
  mapKey: 0,
  submitState: "idle",
  submitError: null,
};

interface SetBoundarySizeAction {
  type: "SET_BOUNDARY_SIZE";
  value: number;
}

interface SetLocationAction {
  type: "SET_LOCATION";
  address:string;
  pin: { lng: number; lat: number };
}

interface SubmitStartAction {
  type: "SUBMIT_START";
}

interface SubmitErrorAction {
  type: "SUBMIT_ERROR";
  message: string;
}

interface SubmitSuccessResetAction {
  type: "SUBMIT_SUCCESS_RESET";
}

type FormAction = | SetBoundarySizeAction | SetLocationAction | SubmitStartAction | SubmitErrorAction | SubmitSuccessResetAction;

function formReducer(state: FormStateProps, action: FormAction): FormStateProps {
  switch (action.type) {
    case "SET_BOUNDARY_SIZE":
      return {
        ...state,
        boundarySize: action.value,
        activeStep: Math.max(state.activeStep, 1),
      };
    case "SET_LOCATION":
      return {
        ...state,
        location: action.address,
        externalPin: action.pin,
        activeStep: Math.max(state.activeStep, 1),
      };
    case "SUBMIT_START":
      return {...state, submitState: "loading", submitError: null };
    case "SUBMIT_ERROR":
      return {...state, submitState: "error", submitError: action.message };
    case "SUBMIT_SUCCESS_RESET":
      return {...initialFormState, mapKey: state.mapKey + 1 };
    default:
      return state;
  }
}

export default function ReportPage() {
  const [form, dispatch] = useReducer(formReducer, initialFormState);
  const statusIndexRef = useRef(-1);
  const [activeRefNum, setActiveRefNum] = useState("");
  const [reports, setReports] = useState<FireReportMapResponse[]>([]);

  useEffect(() => {
    let cancelled = false;
    fetch(`/api/users/reported-fires`)
        .then((res) => res.json())
        .then((data: FireReportMapResponse[]) => {
          if (cancelled) { return };
            const sorted = [...data].sort(
                (a, b) => new Date(b.submitted_at).getTime() - new Date(a.submitted_at).getTime()
            );
            setReports(sorted);
        })
        .catch((err) => {
          if (!cancelled) console.error("Failed to fetch reports", err);
        });
      return () => {
        cancelled = true;
      };
  }, [activeRefNum]);

  function handleBoundarySizeChange(value: number) {
    dispatch({ type: "SET_BOUNDARY_SIZE", value});
  }

  function handleLocationSelect(loc: {lat: number; lng: number; address: string} ) {
    dispatch({ type: "SET_LOCATION", address: loc.address, pin: { lng: loc.lng, lat: loc.lat }});
  }

  function handleLocationSearch(loc: {lat: number; lng: number; address: string} ) {
    dispatch({ type: "SET_LOCATION", address: loc.address, pin: { lng: loc.lng, lat: loc.lat }});
  }

  async function handleSubmit(data: ReportFormData) {
    dispatch({ type: "SUBMIT_START" });
    try {
      let imageUrl: string | undefined = undefined;

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
          lat: form.externalPin?.lat ?? 0,
          lng: form.externalPin?.lng ?? 0,
          boundary_radius: form.boundarySize,
        }),
      });

      if (!res.ok) {
        throw new Error("Failed to submit report");
      }

      const report = await res.json();
      setActiveRefNum(report.reference_number);
      statusIndexRef.current = 0;

      setTimeout(() => {
        dispatch({ type: "SUBMIT_SUCCESS_RESET" });
      }, 1000);
    } catch (err) {
      console.error('Failed to submit report', err);
      dispatch({ type: "SUBMIT_ERROR", message: "Failed to submit report. Please try again." });
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
                  key={form.mapKey}
                  externalPin={form.externalPin}
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
                location={form.location}
                onSubmit={handleSubmit}
                onLocationSearch={handleLocationSearch}
              />
            </div>

            <div className="rounded-lg bg-carbon-side border border-carbon-stroke p-3 overflow-y-auto">
              <h4 className = "mb-2">Report status</h4>
              {form.submitState === "error" && form.submitError && <Alert variant="error" message={form.submitError} />}

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