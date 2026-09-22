import { useState } from 'react';
// import { apiCall } from '../lib/api';
import { mockResources } from '../mockData/Resources';
import type { Capacity, ResourceTable } from '../types/Resource';
import { isResourceFormValid } from '../lib/ValidateResource';
import type { ResourceFormValues } from '../lib/ValidateResource';

function todayLocalISO(): string {
    return new Date().toLocaleDateString('en-CA');
}

function getCapacityUnit(form: ResourceFormValues): Capacity {
    if (form.resource === 'other') {
        return 'other';
    }
    if (form.resource === 'crew') {
        return 'members';
    }
    return 'liters';
}

export function useSubmitResource(){
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    async function submitResource(form: ResourceFormValues, fireRef: string | null ): Promise<ResourceTable | null> {
        if (!form.externalPin || !isResourceFormValid(form)) return null;

        setSubmitting(true);
        setError(null);

        try {
            let otherResource = '';
            let otherCapacity = '';
            if (form.resource === 'other') {
                otherResource = form.otherResource.trim();
                otherCapacity = form.otherCapacity.trim();
            }

            const body: Omit<ResourceTable, 'id' | 'status'> = {
                resource: form.resource,
                otherResource,
                otherCapacity,
                capacity: form.capacity,
                capacityUnit: getCapacityUnit(form),
                availableFrom: form.availableFrom || todayLocalISO(),
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
            // return await apiCall('/api/users/resources', 'POST', body);
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Failed to register resource. Please try again.');
            return null;
        } finally {
            setSubmitting(false);
        }
    }
    return { submitResource, submitting, error };
}
