'use client';

import React, { useReducer, useState } from 'react';
import { useRouter } from 'next/router';
import { FireMap } from '../shared/DynamicUserMap';
import { LOCATION_PLACEHOLDER } from '../reportfire/locationConstants';
import { PageHeader } from '../layout/pageHeader';
import { ResourceDropdown } from './ResourceDropdown';
import type { Resource } from '../../types/Resource';
import { Info } from "./Info";
import { Capacity } from './Capacity';
import { LocationField } from '../reportfire/LocationField';
import { Availability } from './Availability';
import {useSubmitResource } from '../../hooks/useSubmitResource';
import { validateResourceForm } from '../../lib/validateResource';
import type { ResourceFormErrors } from '../../lib/validateResource';

interface RegisterResourceProps {
  showHeaderIcons?: boolean;
}

interface FormStateProps {
  activeStep: number;
  location: string;
  boundarySize: number;
  externalPin: { lng: number; lat: number } | null;
  mapKey: number;
  resource: Resource;
  otherResource: string;
  otherCapacity: string;
  name: string;
  contact: string;
  capacity: number;
  availableFrom: string;
  availableUntil: string;
}

const initialFormState: FormStateProps = {
  activeStep: 0,
  location: LOCATION_PLACEHOLDER,
  boundarySize: 0.2,
  externalPin: null,
  mapKey: 0,
  resource: 'water_tank',
  otherResource: '',
  otherCapacity: '',
  name: '',
  contact: '',
  capacity: 0,
  availableFrom: '',
  availableUntil: '',
};

interface SetLocationAction {
  type: 'SET_LOCATION';
  address: string;
  pin: { lng: number; lat: number };
}

interface SetResourceAction {
  type: 'SET_RESOURCE';
  value: Resource;
}

interface SetOtherResourceAction {
  type: 'SET_OTHER_RESOURCE';
  value: string;
}

interface SetOtherCapacityAction {
  type: 'SET_OTHER_CAPACITY';
  value: string;
}

interface SetNameAction {
  type: 'SET_NAME';
  value: string;
}

interface SetContactAction {
  type: 'SET_CONTACT';
  value: string;
}

interface SetCapacityAction {
  type: 'SET_CAPACITY';
  value: number;
}

interface SetAvailabilityAction {
  type: 'SET_AVAILABILITY';
  value: { availableFrom: string; availableUntil: string };
}

interface ResetAfterSubmitAction {
  type: 'RESET_AFTER_SUBMIT';
}

type FormAction = SetLocationAction | SetResourceAction | SetOtherResourceAction  | SetOtherCapacityAction | SetNameAction | SetContactAction | SetCapacityAction | SetAvailabilityAction | ResetAfterSubmitAction; // | SetBoundarySizeAction ;

function formReducer(state: FormStateProps, action: FormAction): FormStateProps {
  switch (action.type) {
    case 'SET_LOCATION':
      return {
        ...state,
        location: action.address,
        externalPin: action.pin,
        activeStep: Math.max(state.activeStep, 1),
      };
    case 'SET_RESOURCE':
      return { ...state, resource: action.value };
    case 'SET_OTHER_RESOURCE':
      return { ...state, otherResource: action.value };
    case 'SET_OTHER_CAPACITY':
      return { ...state, otherCapacity: action.value };
    case 'SET_NAME':
      return { ...state, name: action.value };
    case 'SET_CONTACT':
      return { ...state, contact: action.value };
    case 'SET_CAPACITY':
      return { ...state, capacity: action.value };
    case 'SET_AVAILABILITY':
      return { ...state, ...action.value }
    case 'RESET_AFTER_SUBMIT':
      return { ...initialFormState, mapKey: state.mapKey + 1 };
    default:
      return state;
  }
}

type CapacityConfig = {
  unit: string;
  min: number;
  max: number;
  label: string;
  helperText: string
};

function getCapacityConfig(resource: Resource, otherCapacity: string): CapacityConfig {
  if (resource === 'crew') {
    return { unit: 'members', min: 0, max: 1000, label: 'Crew Size', helperText: 'Number of people available to respond.',};}
  if (resource === 'other') {
    return { unit: otherCapacity.trim() || 'units', min: 0, max: 150000, label: 'Capacity', helperText: 'Used to calculate total available capacity for your area.',};}
  return { unit: 'L', min: 0, max: 150000, label: 'Water Capacity', helperText: 'Used to calculate total available water capacity',};
}

export default function RegisterResourcePage({ showHeaderIcons = true }: RegisterResourceProps) {
  const [form, dispatch] = useReducer(formReducer, initialFormState);
  const capacityConfig = getCapacityConfig(form.resource, form.otherCapacity);
  const router = useRouter();
  const { submitResource, submitting, error } = useSubmitResource();
  const [showErrors, setShowErrors] = useState(false);
  const errors = validateResourceForm(form);

  let shown: ResourceFormErrors = {};
    if (showErrors) {
      shown = errors;
    }

  function handleLocationSelect(loc: { lat: number; lng: number; address: string }) {
    dispatch({ type: 'SET_LOCATION', address: loc.address, pin: { lng: loc.lng, lat: loc.lat } });
  }

  function handleLocationChange(val: string) {
    dispatch({ type: 'SET_LOCATION', address: val,  pin: form.externalPin ?? { lng: 0, lat: 0 } });
  }

  function handleLocationSearch(loc: { lat: number; lng: number; address: string }) {
    dispatch({ type: 'SET_LOCATION', address: loc.address, pin: { lng: loc.lng, lat: loc.lat } });
  }

  function handleResourceChange(value: Resource){
    dispatch({ type: 'SET_RESOURCE', value });
  }

  function handleOtherResourceChange(value: string){
    dispatch({ type: 'SET_OTHER_RESOURCE', value });
  }

  function handleOtherCapacityChange(value: string){
    dispatch({ type: 'SET_OTHER_CAPACITY', value });
  }

  function handleNameChange(value: string){
    dispatch({ type: 'SET_NAME', value });
  }

  function handleContactChange(value: string){
    dispatch({ type: 'SET_CONTACT', value });
  }

  function handleCapacityChange(value: number) {
    dispatch({ type: 'SET_CAPACITY', value })
  }

  function handleAvailabilityChange(value: {availableFrom: string; availableUntil: string;}) {
    dispatch({ type: 'SET_AVAILABILITY', value });
  }

  function handleCancel() {
    dispatch({ type: 'RESET_AFTER_SUBMIT' });
    setShowErrors(false);
  }

  async function handleSubmit() {
    if(Object.keys(errors).length > 0){
      setShowErrors(true);
      return;
    }

    const created = await submitResource(form);
    if (created){
      dispatch({ type: 'RESET_AFTER_SUBMIT' });
      setShowErrors(false);
      // router.push('/resources');//change to real route
    }
  }

  let submitError = null;
  if (error) {
    submitError = <p className="text-error text-sm mt-3">{error}</p>;
  }

  let submitLabel = 'Register resource';
  if (submitting) {
    submitLabel = 'Registering…';
  }

  return (
    <div className="flex flex-col p-2">
      <header>
        <PageHeader title="Register a Resources" subtitle="Add your water trailer, tank, dam, hydrant, crew or equipment to be used in a fire." showIcons={showHeaderIcons} />
      </header>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 xl:grid-rows-1 mt-4">
        {/* Left Column */}
        <div className="xl:col-span-8 flex flex-col gap-4">
          <div className="rounded-lg bg-carbon-side border border-carbon-stroke flex flex-col overflow-hidden h-96 sm:h-104 lg:h-132 xl:h-150">
            <div className="p-4 border-b border-carbon-card">
              <span className="font-display font-bold tracking-wide uppercase text-lg">
                Pin a Location
              </span>
            </div>
            <div className="flex-1 w-full">
              <FireMap key={form.mapKey} externalPin={form.externalPin} onLocationSelect={handleLocationSelect} showRadius={false} />
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="xl:col-span-4 flex flex-col gap-3">
          <div className="rounded-lg bg-carbon-side border border-carbon-stroke p-3 flex flex-col gap-3">
            <div className="mb-1">
              <h4 className="p-1">What are you registering? </h4>
              <ResourceDropdown value={form.resource} other={form.otherResource} otherCapacity={form.otherCapacity} onChange={handleResourceChange} onChangeOther={handleOtherResourceChange} onChangeOtherCapacity={handleOtherCapacityChange} error={shown.otherResource}/>
            </div>
            <Info name={form.name} contact={form.contact} onNameChange={handleNameChange} onContactChange={handleContactChange} nameError={shown.name} contactError={shown.contact} />
            <Capacity value={form.capacity} unit={capacityConfig.unit} min={capacityConfig.min} max={capacityConfig.max} label={capacityConfig.label} helperText={capacityConfig.helperText} onChange={handleCapacityChange} error={shown.capacity} />
            <div className='mb-3 flex items-center gap-3'>
              <LocationField value={form.location} onChange={handleLocationChange} onValidSelect={handleLocationSearch} error={shown.location} />
            </div>
            <Availability value={{ availableFrom: form.availableFrom, availableUntil: form.availableUntil }} onChange={handleAvailabilityChange} />

            {submitError}
            <div className="flex items-center justify-between gap-3 mt-4">
              <button type="button" className="btn btn-ghost" onClick={handleCancel} disabled={submitting}>
                Cancel
              </button>
              <button type="button" className="btn btn-primary" onClick={handleSubmit} disabled={submitting}>
                {submitLabel}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
