import React, { useState } from 'react';
import { useRouter } from 'next/router';
import Image from 'next/image';
import { apiCall } from '../lib/api';

interface RegisterForm {
  name: string;
  surname: string;
  email: string;
  idNumber: string;
  licenceNumber: string;
  password: string;
  confirmPassword: string;
  role: 'User' | 'Firefighter';
}

interface FormErrors {
  name?: string;
  surname?: string;
  email?: string;
  idNumber?: string;
  password?: string;
  confirmPassword?: string;
  licenceNumber?: string;
}

function validateEmail(email: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function validateSAId(id: string) {
  return /^\d{13}$/.test(id);
}

export default function Register() {
  const [form, setForm] = useState<RegisterForm>({
    name: '',
    surname: '',
    email: '',
    idNumber: '',
    licenceNumber: '',
    password: '',
    confirmPassword: '',
    role: 'User',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [apiError, setApiError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
    setErrors(prev => ({ ...prev, [name]: undefined }));
  };

  const validate = (): boolean => {
    const newErrors: FormErrors = {};

    if (!form.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!form.surname.trim()) {
      newErrors.surname = 'Surname is required';
    }

    if (!form.email) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(form.email)) {
      newErrors.email = 'Enter a valid email address';
    }

    if (!form.idNumber) {
      newErrors.idNumber = 'ID/Passport number is required';
    } else if (!validateSAId(form.idNumber)) {
      newErrors.idNumber = 'SA ID must be exactly 13 digits';
    }

    if (!form.password) {
      newErrors.password = 'Password is required';
    } else if (form.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    } else if (!/[A-Z]/.test(form.password)) {
      newErrors.password = 'Password must contain at least one uppercase letter';
    } else if (!/[0-9]/.test(form.password)) {
      newErrors.password = 'Password must contain at least one number';
    }

    if (!form.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (form.password !== form.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    if (form.role === 'Firefighter' && !form.licenceNumber.trim()) {
      newErrors.licenceNumber = 'Licence number is required for firefighters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setApiError('');
    if (!validate()) {
      return;
    }
    setIsLoading(true);
    try {
      const res = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
        email: form.email,
        password: form.password,
        name: form.name,
        surname: form.surname,
        id_number: form.idNumber,
        licence_number: form.role === 'Firefighter' ? form.licenceNumber : null,
        role: form.role,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Something went wrong');
      router.push('/guests');
    } catch (err: any) {
      setApiError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const fieldClass = (hasError?: string) =>
    `w-full px-3 py-2 bg-carbon-input border rounded-md text-neutral focus:outline-none focus:ring-1 focus:ring-primary ${
      hasError ? 'border-flare' : 'border-carbon-stroke'
    }`;

  return (
    <div className="relative min-h-screen bg-carbon-bg overflow-hidden">
      <div className="global-atmos">
        <div className="ga-bloom-primary" />
        <div className="ga-bloom-secondary" />
        <div className="ga-bloom-tertiary" />
      </div>

      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen p-4">
        <div className="mb-8">
          <Image
            src="/images/logo-large.png"
            alt="Fire Spread Prediction Logo"
            width={450}
            height={420}
            className="mx-auto"
          />
        </div>

        <div className="w-full max-w-3xl bg-carbon-card border border-carbon-stroke rounded-xl p-6 shadow-2xl backdrop-blur-sm">
          <h2 className="text-2xl font-bold text-neutral text-center mb-6">Create account</h2>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-3" noValidate>

            <div>
              <label htmlFor="name" className="block text-sm text-white/60">Name</label>
              <input id="name" name="name" placeholder="Name" value={form.name} onChange={handleChange} className={fieldClass(errors.name)} />
              {errors.name && <p className="text-flare text-xs mt-1">{errors.name}</p>}
            </div>

            <div>
              <label htmlFor="surname" className="block text-sm text-white/60">Surname</label>
              <input id="surname" name="surname" placeholder="Surname" value={form.surname} onChange={handleChange} className={fieldClass(errors.surname)} />
              {errors.surname && <p className="text-flare text-xs mt-1">{errors.surname}</p>}
            </div>

            <div className="md:col-span-2">
              <label htmlFor="email" className="block text-sm text-white/60">Email</label>
              <input id="email" type="email" name="email" placeholder="Email" value={form.email} onChange={handleChange} className={fieldClass(errors.email)} />
              {errors.email && <p className="text-flare text-xs mt-1">{errors.email}</p>}
            </div>

            <div className="md:col-span-2">
              <label htmlFor="idNumber" className="block text-sm text-white/60">ID/Passport Number</label>
              <input id="idNumber" name="idNumber" placeholder="13-digit SA ID" value={form.idNumber} onChange={handleChange} className={fieldClass(errors.idNumber)} />
              {errors.idNumber && <p className="text-flare text-xs mt-1">{errors.idNumber}</p>}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm text-white/60">Password</label>
              <input id="password" type="password" name="password" placeholder="Min 8 chars, 1 uppercase, 1 number" value={form.password} onChange={handleChange} className={fieldClass(errors.password)} />
              {errors.password && <p className="text-flare text-xs mt-1">{errors.password}</p>}
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm text-white/60">Confirm Password</label>
              <input id="confirmPassword" type="password" name="confirmPassword" placeholder="Repeat password" value={form.confirmPassword} onChange={handleChange} className={fieldClass(errors.confirmPassword)} />
              {errors.confirmPassword && <p className="text-flare text-xs mt-1">{errors.confirmPassword}</p>}
            </div>

            <div className="md:col-span-2">
              <label htmlFor="role" className="block text-sm text-white/60">Role</label>
              <select id="role" name="role" value={form.role} onChange={handleChange} className={fieldClass()}>
                <option>User</option>
                <option>Firefighter</option>
              </select>
            </div>

            {form.role === 'Firefighter' && (
              <div className="md:col-span-2">
                <label htmlFor="licenceNumber" className="block text-sm text-white/60">Licence Number</label>
                <input id="licenceNumber" name="licenceNumber" placeholder="Licence number" value={form.licenceNumber} onChange={handleChange} className={fieldClass(errors.licenceNumber)} />
                {errors.licenceNumber && <p className="text-flare text-xs mt-1">{errors.licenceNumber}</p>}
              </div>
            )}

            {apiError && <div className="md:col-span-2 bg-flare/10 border border-flare/50 text-flare text-sm p-2 rounded">{apiError}</div>}

            <div className="md:col-span-2 mt-2">
              <button type="submit" disabled={isLoading} className="w-full py-2 bg-ember hover:bg-deep text-white font-medium rounded-md transition disabled:opacity-50">
                {isLoading ? 'Registering...' : 'Register now'}
              </button>
            </div>

          </form>
        </div>
      </div>
    </div>
  );
}