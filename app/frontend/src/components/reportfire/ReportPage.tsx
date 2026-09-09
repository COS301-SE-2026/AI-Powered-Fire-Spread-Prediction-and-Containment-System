'use client';

import React, { useReducer } from 'react';
import StepIndicator from './StepIndicator';
import ReportDetailsForm, { type ReportFormData } from './ReportDetailsForm';
import ReportStatus from './ReportStatus';
import { FireMap } from '../shared/DynamicUserMap';
import { Alert } from '../shared/Alerts';
import { LOCATION_PLACEHOLDER } from './locationConstants';
import { useUserReports } from '../../hooks/useUserReports';
import { useSubmitReport } from '../../hooks/useSubmitReport';
import { PageHeader } from '../layout/pageHeader';

interface ReportPageProps {
  showHeaderIcons?: boolean;
}

interface FormStateProps {
  activeStep: number;
  location: string;
  boundarySize: number;
  externalPin: { lng: number; lat: number } | null;
  mapKey: number;
}

const initialFormState: FormStateProps = {
  activeStep: 0,
  location: LOCATION_PLACEHOLDER,
  boundarySize: 0.2,
  externalPin: null,
  mapKey: 0,
};

interface SetBoundarySizeAction {
  type: 'SET_BOUNDARY_SIZE';
  value: number;
}

interface SetLocationAction {
  type: 'SET_LOCATION';
  address: string;
  pin: { lng: number; lat: number };
}

interface ResetAfterSubmitAction {
  type: 'RESET_AFTER_SUBMIT';
}

type FormAction = SetBoundarySizeAction | SetLocationAction | ResetAfterSubmitAction;

function formReducer(state: FormStateProps, action: FormAction): FormStateProps {
  switch (action.type) {
    case 'SET_BOUNDARY_SIZE':
      return {
        ...state,
        boundarySize: action.value,
        activeStep: Math.max(state.activeStep, 1),
      };
    case 'SET_LOCATION':
      return {
        ...state,
        location: action.address,
        externalPin: action.pin,
        activeStep: Math.max(state.activeStep, 1),
      };
    case 'RESET_AFTER_SUBMIT':
      return { ...initialFormState, mapKey: state.mapKey + 1 };
    default:
      return state;
  }
}

export default function ReportPage({ showHeaderIcons = true }: ReportPageProps) {
  const [form, dispatch] = useReducer(formReducer, initialFormState);
  const { reports, refetch } = useUserReports();
  const { submitReport, submitting, error } = useSubmitReport();

  function handleBoundarySizeChange(value: number) {
    dispatch({ type: 'SET_BOUNDARY_SIZE', value });
  }

  function handleLocationSelect(loc: { lat: number; lng: number; address: string }) {
    dispatch({ type: 'SET_LOCATION', address: loc.address, pin: { lng: loc.lng, lat: loc.lat } });
  }

  function handleLocationSearch(loc: { lat: number; lng: number; address: string }) {
    dispatch({ type: 'SET_LOCATION', address: loc.address, pin: { lng: loc.lng, lat: loc.lat } });
  }

  async function handleSubmit(data: ReportFormData) {
    const report = await submitReport({
      location: data.location,
      description: data.description,
      photo: data.photo,
      lat: form.externalPin?.lat ?? 0,
      lng: form.externalPin?.lng ?? 0,
      boundaryRadius: form.boundarySize,
    });

    if (!report) return;

    await refetch();

    setTimeout(() => {
      dispatch({ type: 'RESET_AFTER_SUBMIT' });
    }, 1000);
  }

  return (
    <div className="flex flex-col p-2">
      <header>
        <PageHeader title="Report a fire" showIcons={showHeaderIcons} />
        <div className="mt-2">
          <StepIndicator />
        </div>
      </header>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 xl:grid-rows-1 mt-4">
        {/* Left Column */}
        <div className="xl:col-span-8 flex flex-col gap-4">
          <div className="rounded-lg bg-carbon-side border border-carbon-stroke flex flex-col overflow-hidden h-96 sm:h-104 lg:h-132 xl:h-150">
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
            <h4 className="mb-2">Report status</h4>
            {error && <Alert variant="error" message={error} />}

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
