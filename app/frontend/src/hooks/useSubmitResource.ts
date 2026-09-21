import { useState } from 'react';
import { apiCall } from '../lib/api';
import type { ResourceInput, ResourceTable } from '../types/Resource';
import { isResourceFormValid } from '../lib/validateResource';
import type { ResourceFormValues } from '../lib/validateResource';

function todayLocalISO(): string {
    return new Date().toLocaleDateString('en-CA');
}

export function useSubmitResource(){
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    async function submitResource(form: ResourceFormValues): Promise<ResourceTable | null> {
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

            const body: ResourceInput = {
                resource: form.resource,
                otherResource,
                otherCapacity,
                capacity: form.capacity,
                availableFrom: form.availableFrom || todayLocalISO(),
                availableUntil: form.availableUntil,
                location: form.location,
                externalPin: form.externalPin,
                name: form.name.trim(),
                contact: form.contact.trim(),
            };
            return await apiCall('/api/users/resources', 'POST', body);
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Failed to register resource. Please try again.');
            return null;
        } finally {
            setSubmitting(false);
        }
    }
    return { submitResource, submitting, error };
}
