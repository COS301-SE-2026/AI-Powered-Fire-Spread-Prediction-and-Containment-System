import React, { useState } from 'react';
import { useRouter } from 'next/router';
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
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
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
      router.push(`/login\?registered=true/`);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#080B12] flex items-center justify-center p-4">
      <div className="w-full max-w-3xl bg-[#12151E] border border-white/10 rounded-xl p-6">
        <h2 className="text-2xl font-bold text-[#EDEAE5] text-center mb-6">Create account</h2>
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="name" className="block text-sm text-white/60">Name</label>
            <input id="name" name="name" placeholder="Name" value={form.name} onChange={handleChange} className="w-full px-3 py-2 bg-[#0B0E14] border border-white/10 rounded-md text-[#EDEAE5]" required />
          </div>
          <div>
            <label htmlFor="surname" className="block text-sm text-white/60">Surname</label>
            <input id="surname" name="surname" placeholder="Surname" value={form.surname} onChange={handleChange} className="w-full px-3 py-2 bg-[#0B0E14] border border-white/10 rounded-md text-[#EDEAE5]" required />
          </div>
          <div className="md:col-span-2">
            <label htmlFor="email" className="block text-sm text-white/60">Email</label>
            <input id="email" type="email" name="email" placeholder="Email" value={form.email} onChange={handleChange} className="w-full px-3 py-2 bg-[#0B0E14] border border-white/10 rounded-md text-[#EDEAE5]" required />
          </div>
          <div>
            <label htmlFor="idNumber" className="block text-sm text-white/60">ID/Passport Number</label>
            <input id="idNumber" name="idNumber" placeholder="ID/Passport Number" value={form.idNumber} onChange={handleChange} className="w-full px-3 py-2 bg-[#0B0E14] border border-white/10 rounded-md text-[#EDEAE5]" required />
          </div>
          <div className="md:col-span-2">
            <label htmlFor="password" className="block text-sm text-white/60">Password</label>
            <input id="password" type="password" name="password" placeholder="Password" value={form.password} onChange={handleChange} className="w-full px-3 py-2 bg-[#0B0E14] border border-white/10 rounded-md text-[#EDEAE5]" required />
          </div>
          <div className="md:col-span-2">
            <label htmlFor="role" className="block text-sm text-white/60">Role</label>
            <select id="role" name="role" value={form.role} onChange={handleChange} className="w-full px-3 py-2 bg-[#0B0E14] border border-white/10 rounded-md text-[#EDEAE5]">
              <option>User</option>
              <option>Firefighter</option>
            </select>
          </div>
          {form.role === 'Firefighter' && (
            <div className="md:col-span-2">
              <label htmlFor="licenceNumber" className="block text-sm text-white/60">Licence number</label>
              <input id="licenceNumber" name="licenceNumber" placeholder="Licence number" value={form.licenceNumber} onChange={handleChange} className="w-full px-3 py-2 bg-[#0B0E14] border border-white/10 rounded-md text-[#EDEAE5]" required />
            </div>
          )}
          {error && <div className="col-span-2 bg-red-500/10 border border-red-500/50 text-red-400 text-sm p-2 rounded">{error}</div>}
          <div className="col-span-2 mt-2">
            <button type="submit" disabled={isLoading} className="w-full py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-md transition">
              {isLoading ? 'Registering...' : 'Register now'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}