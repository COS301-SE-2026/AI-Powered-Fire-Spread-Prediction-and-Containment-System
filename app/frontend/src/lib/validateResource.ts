import type { ResourceInput } from '../types/Resource';

export type ResourceFormValues = Omit<ResourceInput, 'externalPin' | 'fireRef'> & {
    externalPin: { lat: number; lng: number; } | null;
}

export type ResourceFormErrors = Partial<Record<'location' | 'otherResource' | 'name' | 'contact' | 'capacity', string>>;

export function validateResourceForm(form: ResourceFormValues): ResourceFormErrors {
    const errors: ResourceFormErrors = {};

    //location validation
    const hasPin = form.externalPin !== null && (form.externalPin.lat !== 0 || form.externalPin.lng !== 0);
    if (!hasPin){
        errors.location = 'Pin a location on the map or search for an address.';
    }

    //resource type validation
    if (form.resource === 'other' && form.otherResource.trim() === '') {
        errors.otherResource = 'Tell us what type of resource this is.';
    }

    //name validation
    if (form.name.trim() === '') {
        errors.name = 'Enter a name for this resource.';
    } else if (/^\d+$/.test(form.name.trim())) {
        // This checks if the name consists ONLY of digits
        errors.name = 'Name cannot be only numbers.';
    } else if (form.name.trim().length < 3) {
        errors.name = 'Name must be at least 3 characters long.';
    }

    //contact number validation
    const digits = form.contact.replaceAll(/\D/g, '');
    const isLocal = digits.length === 10 && digits.startsWith('0');
    const isIntl = digits.length === 11 && digits.startsWith('27');
    const isRepeated = /^(\d)\1+$/.test(digits);

    if (!isLocal && !isIntl) {
        errors.contact = 'Enter a valid 10-digit number.';
    } else if (isRepeated) {
        errors.contact = 'This phone number is invalid.';
    }

    //capacity validation
    if (isNaN(form.capacity) || form.capacity <= 0) {
        errors.capacity = 'Capacity must be a positive number.';
    }
    return errors;
}

export function isResourceFormValid(form: ResourceFormValues): boolean {
    return Object.keys(validateResourceForm(form)).length === 0;
}