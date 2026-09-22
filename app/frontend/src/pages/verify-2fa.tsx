import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Image from 'next/image';
import { apiCall } from '../lib/api';

export default function Verify2FA() {
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  
  const [authData, setAuthData] = useState<{
    email: string;
    otpauthUrl?: string;
    registrationToken?: string;
  }>({email: ''});

  useEffect(() => {
    if(!router.isReady) return;

    let email = (router.query.email as string) || '';
    let otpauthUrl = (router.query.otpauth_url as string) || '';
    let registrationToken = (router.query.registration_token as string) || '';

    if(typeof window !== 'undefined'){
      const stored = sessionStorage.getItem('pending_2fa');
      if(stored){
        try{
          const parsed = JSON.parse(stored);
          email = email || parsed.email || '';
          otpauthUrl = otpauthUrl || parsed.otpauthUrl || parsed.otpauth_url || '';
          registrationToken = registrationToken || parsed.registrationToken || parsed.registration_token || '';
        }catch {
          // eslint-disable-next-line no-empty
        }
      }
    }

    setAuthData({email, otpauthUrl, registrationToken})
  }, [router.isReady, router.query]);

  const isRegistration = Boolean(authData.registrationToken);
  const isValidSession = Boolean(authData.email || authData.registrationToken);
  const hasQrSetup = Boolean(authData.otpauthUrl);

  const qrCodeSrc = hasQrSetup
    ? `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(authData.otpauthUrl as string)}`
    : '';

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!code || code.length !== 6) {
      setError('Enter the 6‑digit code');
      return;
    }
    setIsLoading(true);
    setError('');

    try {
      let data: {role?: string; pending_approval?: boolean};

      if(isRegistration){
        data = await apiCall('/api/auth/complete-registration', 'POST', {
          registration_token: authData.registrationToken,
          code,
        });
      }else{
        data = await apiCall('/api/auth/verify-2fa', 'POST', {
          username: authData.email,
          code,
        });
      }

      if(typeof window !== 'undefined'){
        sessionStorage.removeItem('pending_2fa');
      }

      if(data?.pending_approval){
        router.push('/users/live-map');
        return;
      }

      const roleRedirects: Record<string, string> = {
        admin: '/admin/dashboard',
        firefighter: '/firefighter/dashboard',
        user: '/users/live-map',
      };

      if (data.role) {
        router.push(roleRedirects[data.role] ?? '/login');
      } else {
        setError('Verification failed');
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Verification failed. Please try again.');
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
            height={450}
            className="mx-auto"
          />
        </div>

        <div className="w-full max-w-md bg-carbon-card border border-carbon-stroke rounded-xl p-6 text-center shadow-2xl backdrop-blur-sm">
          <h2 className="text-2xl font-bold text-text-primary mb-2">Two‑Factor Authentication</h2>
          {!isValidSession ? (
            <>
              <p className="text-white/60 text-sm mb-4">
                No active session found. Please log in or register again.
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
              {hasQrSetup && (
                <>
                  <p className="text-white/60 text-sm mb-4">
                    Scann this QR code with your authenticator app (Google Authenticator, Authy,
                    etc.), then enter the 6-digit code below.
                  </p>
                  <div className="flex justify-center mb-4">
                    <img
                      src={qrCodeSrc}
                      alt="2FA QR Code"
                      width={220}
                      height={220}
                      className="rounded-md border border-carbon-stroke"
                    />
                  </div>
                  <a href={authData.otpauthUrl as string} className='block text-sm text-primary hover:text-ember underline mb-4'>
                    On this device? Tab here to open your authenticator app
                  </a>
                </>
              )}

              {!hasQrSetup && (
                <p className="text-white/60 text-sm mb-4">
                  Enter the 6‑digit code from your authenticator app
                </p>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <input
                  type="text"
                  maxLength={6}
                  placeholder="000000"
                  className="w-full px-3 py-2 bg-carbon-input border border-carbon-stroke rounded-md text-text-primary text-center text-2xl tracking-widest focus:outline-none focus:ring-1 focus:ring-primary"
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
