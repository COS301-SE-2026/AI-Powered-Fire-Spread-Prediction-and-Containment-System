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
  role: 'User' | 'Firefighter';
}

export default function Register() {
  const [form, setForm] = useState<RegisterForm>({
    name: '',
    surname: '',
    email: '',
    idNumber: '',
    licenceNumber: '',
    password: '',
    role: 'User',
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    // Clear the error when user starts typing again
    if (error) setError('');
  };

  const validateForm = (): string | null => {
    // Name
    if (!form.name.trim()) return 'Name is required';
    if (form.name.length < 2) return 'Name must be at least 2 characters';
    // Surname
    if (!form.surname.trim()) return 'Surname is required';
    if (form.surname.length < 2) return 'Surname must be at least 2 characters';
    // Email
    if (!form.email.trim()) return 'Email is required';
    //yes, I found the regex online
      const emailRegex = /^(?:[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$/i;
    if (!emailRegex.test(form.email)) return 'Please enter a valid email address';
    // ID/Passport
    if (!form.idNumber.trim()) return 'ID/Passport number is required';
    if (form.idNumber.length < 13) return 'ID number must be at least 13 characters';
    // Password
    if (!form.password) return 'Password is required';
    if (form.password.length < 8) return 'Password must be at least 8 characters';
    if (!/[A-Za-z]/.test(form.password)) return 'Password must contain at least one letter';
    if (!/\d/.test(form.password)) return 'Password must contain at least one number';
    // Licence number (only if Firefighter)
    if (form.role === 'Firefighter' && !form.licenceNumber.trim()) {
      return 'Licence number is required for firefighters';
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }
    setError('');
    setIsLoading(true);
    try {
      await apiCall('/api/register', 'POST', {
        email: form.email,
        password: form.password,
        name: form.name,
        surname: form.surname,
        id_number: form.idNumber,
        licence_number: form.role === 'Firefighter' ? form.licenceNumber : null,
        role: form.role,
      });
      router.push('/login?registered=true');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

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
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-1">
            <div>
              <label htmlFor="name" className="block text-sm text-white/60">Name</label>
              <input
                id="name"
                name="name"
                placeholder="Name"
                value={form.name}
                onChange={handleChange}
                className="w-full px-3 py-2 bg-carbon-input border border-carbon-stroke rounded-md text-neutral focus:outline-none focus:ring-1 focus:ring-primary"
                required
              />
            </div>
            <div>
              <label htmlFor="surname" className="block text-sm text-white/60">Surname</label>
              <input
                id="surname"
                name="surname"
                placeholder="Surname"
                value={form.surname}
                onChange={handleChange}
                className="w-full px-3 py-2 bg-carbon-input border border-carbon-stroke rounded-md text-neutral focus:outline-none focus:ring-1 focus:ring-primary"
                required
              />
            </div>
            <div className="md:col-span-2">
              <label htmlFor="email" className="block text-sm text-white/60">Email</label>
              <input
                id="email"
                type="email"
                name="email"
                placeholder="Email"
                value={form.email}
                onChange={handleChange}
                className="w-full px-3 py-2 bg-carbon-input border border-carbon-stroke rounded-md text-neutral focus:outline-none focus:ring-1 focus:ring-primary"
                required
              />
            </div>
            <div>
              <label htmlFor="idNumber" className="block text-sm text-white/60">ID/Passport Number</label>
              <input
                id="idNumber"
                name="idNumber"
                placeholder="ID/Passport Number"
                value={form.idNumber}
                onChange={handleChange}
                className="w-full px-3 py-2 bg-carbon-input border border-carbon-stroke rounded-md text-neutral focus:outline-none focus:ring-1 focus:ring-primary"
                required
              />
            </div>
            <div className="md:col-span-2">
              <label htmlFor="password" className="block text-sm text-white/60">Password</label>
              <input
                id="password"
                type="password"
                name="password"
                placeholder="Password"
                value={form.password}
                onChange={handleChange}
                className="w-full px-3 py-2 bg-carbon-input border border-carbon-stroke rounded-md text-neutral focus:outline-none focus:ring-1 focus:ring-primary"
                required
              />
            </div>
            <div className="md:col-span-2">
              <label htmlFor="role" className="block text-sm text-white/60">Role</label>
              <select
                id="role"
                name="role"
                value={form.role}
                onChange={handleChange}
                className="w-full px-3 py-2 bg-carbon-input border border-carbon-stroke rounded-md text-neutral focus:outline-none focus:ring-1 focus:ring-primary"
              >
                <option>User</option>
                <option>Firefighter</option>
              </select>
            </div>
            {form.role === 'Firefighter' && (
              <div className="md:col-span-2">
                <label htmlFor="licenceNumber" className="block text-sm text-white/60">Licence number</label>
                <input
                  id="licenceNumber"
                  name="licenceNumber"
                  placeholder="Licence number"
                  value={form.licenceNumber}
                  onChange={handleChange}
                  className="w-full px-3 py-2 bg-carbon-input border border-carbon-stroke rounded-md text-neutral focus:outline-none focus:ring-1 focus:ring-primary"
                  required={form.role === 'Firefighter'}
                />
              </div>
            )}
            {error && <div className="col-span-2 bg-error/10 border border-error/50 text-torch text-sm p-2 rounded">{error}</div>}
            <div className="col-span-2 mt-2">
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