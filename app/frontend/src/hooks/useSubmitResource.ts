import { useState } from 'react';
import { apiCall } from '../lib/api';
import { mockResources } from '../mockData/Resources';
import type { ResourceTable, ResourceInput } from '../types/Resource';

export type ResourceFormValues = Omit<ResourceInput, 'externalPin' | 'fireRef'> & {
  externalPin: { lat: number; lng: number } | null;
};

export function isResourceFormValid(form: ResourceFormValues): boolean {
  const hasPin =
    form.externalPin !== null &&
    (form.externalPin.lat !== 0 || form.externalPin.lng !== 0);

  return (
    hasPin &&
    form.name.trim() !== '' &&
    form.contact.trim() !== '' &&
    form.capacity > 0 &&
    (form.resource !== 'other' || form.otherResource.trim() !== '')
  );
}

export function useSubmitResource(){
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    async function submitResource(form: ResourceFormValues, fireRef: string | null ): Promise<ResourceTable | null> {
        if (!form.externalPin || !isResourceFormValid(form)) return null;

        setSubmitting(true);
        setError(null);

        try {
            const isOther = form.resource === 'other';
            const body: Omit<ResourceTable, 'id' | 'status'> = {
                resource: form.resource,
                otherResource: isOther ? form.otherResource.trim() : '',
                otherCapacity: isOther ? form.otherCapacity.trim() : '',
                capacity: form.capacity,
                capacityUnit: isOther ? 'other' : form.resource === 'crew' ? 'members' : 'liters',
                availableFrom: form.availableFrom,
                availableUntil: form.availableUntil,
                location: form.location,
                externalPin: form.externalPin,
                name: form.name.trim(),
                contact: form.contact.trim(),
                fireRef,
            };
            // MOCK: delete these two lines when the backend is ready...
            const created: ResourceTable = { ...body, id: crypto.randomUUID(), status: 'available' };
            mockResources.push(created);
            return created;

            // ...and uncomment this one
            // return await apiCall('/api/users/resources', 'POST', input);
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Failed to register resource. Please try again.');
            return null;
        } finally {
            setSubmitting(false);
        }
    }
    return { submitResource, submitting, error };
}
