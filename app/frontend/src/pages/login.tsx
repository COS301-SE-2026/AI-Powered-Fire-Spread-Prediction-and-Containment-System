import React, { useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import Image from 'next/image';
import { apiCall } from '../lib/api';

function validateEmail(email: string){
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});
  const [apiError, setApiError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const validate = () => {
    const newErrors: { email?: string; password?: string} = {};
    if(!email){
      newErrors.email = 'Email is required';
    }else if(!validateEmail(email)){ 
      newErrors.email = 'Enter a valid email address';
    }
    if (!password) {
      newErrors.password = 'Password is required';
    }else if(password.length < 6){
      newErrors.password = 'Password must be at least 6 characters';
    } 

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setApiError('');
    if(!validate()){
      return;
    }
    setIsLoading(true);
    try {
      const data = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      }).then(res => res.json());
      if (data.access_token) {
        localStorage.setItem('token', data.access_token);
        router.push('/guests');
      } else {
        setApiError('Unexpected response');
      }
    } catch (err: any) {
        setApiError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGuest = () => {
    localStorage.setItem('token', 'guest-token-' + Date.now());
    router.push('/guests');
  };

  const fieldClass = (hasError?: string) =>
    `w-full px-3 py-2 bg-carbon-input border rounded-md text-neutral focus:outline-none focus:ring-1 focus:ring-primary ${
      hasError ? 'border-flare' : 'border-carbon-stroke'
    }`

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
            height={450}
            className="mx-auto"
          />
        </div>
        <div className="w-full max-w-md bg-carbon-card border border-carbon-stroke rounded-xl p-6 shadow-2xl backdrop-blur-sm">
          <h2 className="text-2xl font-bold text-neutral text-center mb-6">Welcome back</h2>
          <form onSubmit={handleLogin} className="space-y-4" noValidate>
            <div>
              <label htmlFor="email" className="block text-sm text-white/60 mb-1">Email</label>
              <input
                id="email"
                type="email"
                placeholder="example@something.co.za"
                className={fieldClass(errors.email)}
                value={email}
                onChange={(e) => { setEmail(e.target.value); setErrors(prev => ({ ...prev, email: undefined })); }}
              />
              {errors.email && <p className="text-flare text-xs mt-1">{errors.email}</p>}
            </div>
            <div>
              <label htmlFor="password" className="block text-sm text-white/60 mb-1">Password</label>
              <input
                id="password"
                type="password"
                placeholder="••••••••"
                className={fieldClass(errors.password)}
                value={password}
                onChange={(e) => { setPassword(e.target.value); setErrors(prev => ({ ...prev, password: undefined })); }}
              />
              {errors.password && <p className="text-flare text-xs mt-1">{errors.password}</p>}
            </div>
            {apiError && <div className="bg-flare/10 border border-flare/50 text-flare text-sm p-2 rounded">{apiError}</div>}
            <button type="submit" disabled={isLoading} className="w-full py-2 bg-ember hover:bg-deep text-white font-medium rounded-md transition disabled:opacity-50">
              {isLoading ? 'Logging in...' : 'Login'}
            </button>
            <Link href="/register" className="block w-full py-2 text-center border border-carbon-stroke hover:bg-carbon-elevated text-white/90 rounded-md transition">
              Register
            </Link>
            <button type="button" onClick={handleGuest} className="w-full py-2 text-white/80 hover:text-white transition">
              Sign in as Guest
            </button>
          </form>
          <div className="text-center mt-4 text-sm text-white/40">
            <Link href="/forgot-password" className="hover:text-primary">Forgot password? </Link>
            <Link href="/cant-login" className="hover:text-primary"> Can&apos;t log in?</Link>
          </div>
        </div>
      </div>
    </div>
  );
}