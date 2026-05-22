import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Image from 'next/image';
import { apiCall } from '../lib/api';

export default function Verify2FA() {
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const { email } = router.query;

  // Remove the automatic redirect – instead show a message
  // Optionally, you can still redirect after a few seconds, but let the user see the page.

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!code || code.length !== 6) {
      setError('Enter the 6‑digit code');
      return;
    }
    if (!email || typeof email !== 'string') {
      setError('No email provided. Please go back and login again.');
      return;
    }
    setIsLoading(true);
    setError('');
    try {
      const data = await apiCall('/auth/verify-2fa', 'POST', {
        username: email,
        code,
      });
      if (data.access_token) {
        localStorage.setItem('token', data.access_token);
        router.push('/dashboard');
      } else {
        setError('Verification failed');
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const isValidEmail = email && typeof email === 'string';

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

        <div className="w-full max-w-md bg-carbon-card border border-carbon-stroke rounded-xl p-6 text-center shadow-2xl backdrop-blur-sm">
          <h2 className="text-2xl font-bold text-neutral mb-2">Two‑Factor Authentication</h2>
          {!isValidEmail ? (
            <>
              <p className="text-white/60 text-sm mb-4">
                No verification email provided. Please log in again.
              </p>
              <button
                onClick={() => router.push('/login')}
                className="w-full py-2 bg-primary hover:bg-ember text-white font-medium rounded-md transition"
              >
                Back to Login
              </button>
            </>
          ) : (
            <>
              <p className="text-white/60 text-sm mb-4">
                Enter the 6‑digit code from your authenticator app
              </p>
              <form onSubmit={handleSubmit} className="space-y-4">
                <input
                  type="text"
                  maxLength={6}
                  placeholder="000000"
                  className="w-full px-3 py-2 bg-carbon-input border border-carbon-stroke rounded-md text-neutral text-center text-2xl tracking-widest focus:outline-none focus:ring-1 focus:ring-primary"
                  value={code}
                  onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                  required
                />
                {error && (
                  <div className="bg-error/10 border border-error/50 text-error text-sm p-2 rounded">
                    {error}
                  </div>
                )}
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full py-2 bg-ember hover:bg-deep text-white font-medium rounded-md transition disabled:opacity-50"
                >
                  {isLoading ? 'Verifying...' : 'Verify'}
                </button>
              </form>
              <button
                onClick={() => router.push('/login')}
                className="mt-4 text-sm text-white/40 hover:text-primary"
              >
                Back to login
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}