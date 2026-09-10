import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import Image from 'next/image';
import PasswordInput from '../components/shared/PasswordInput';
import { useAuth } from '../hooks/useAuth';

function validateEmail(email: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

const fieldClass = (hasError?: string) => {
  if (hasError) {
    return 'input input-error w-full';
  }
  return 'input input-neutral focus:border-primary w-full';
};

const ROLE_REDIRECTS: Record<string, string> = {
  admin: '/admin/dashboard',
  firefighter: '/firefighter/dashboard',
  user: '/users/live-map',
};

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});
  const [apiError, setApiError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const { isAuth, role, isLoading: isAuthLoading } = useAuth();

  useEffect(() => {
    if (!isAuthLoading && isAuth && role) {
      router.push(ROLE_REDIRECTS[role] ?? '/');
    }
  }, [isAuthLoading, isAuth, role, router]);

  const validate = () => {
    const newErrors: { email?: string; password?: string } = {};
    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(email)) {
      newErrors.email = 'Enter a valid email address';
    }
    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const [cooldown, setCooldown] = useState(0);

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setApiError('');
    if (!validate()) {
      return;
    }
    setIsLoading(true);
    try {
      const res = await fetch(`/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include', // needed so browser stores httpOnly cookie
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const errBody = await res.json().catch(() => null);
        setApiError(errBody?.detail || 'Login failed. Email or password incorrect');

        const match = errBody?.detail?.match(/(\d+)\s*seconds?/);
        if (match) {
          setCooldown(parseInt(match[1], 10));
        }
        return;
      }

      const data = await res.json();

      if (data.requires_2fa) {
        router.push(`/verify-2fa?email=${encodeURIComponent(data.email)}`);
        return;
      }

      sessionStorage.setItem('justLoggedIn', '1');
      window.location.href = ROLE_REDIRECTS[data.role] ?? '/login';
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : 'Login failed. Email or password incorrect.';
      setApiError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGuest = () => {
    router.push('/guests/live-map');
  };

  useEffect(() => {
    if (cooldown <= 0) return;
    const timer = setInterval(() => {
      setCooldown((prev) => (prev > 1 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [cooldown]);

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
          <h2 className="text-2xl font-bold text-text-primary text-center mb-6">Welcome back</h2>
          <form onSubmit={handleLogin} className="space-y-4" noValidate>
            <div>
              <label htmlFor="email" className="block text-sm text-white/60 mb-1">
                Email
              </label>
              <input
                id="email"
                type="email"
                placeholder="example@something.co.za"
                className={fieldClass(errors.email)}
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setErrors((prev) => ({ ...prev, email: undefined }));
                }}
              />
              {errors.email && <p className="text-flare text-xs mt-1">{errors.email}</p>}
            </div>
            <div>
              <label htmlFor="password" className="block text-sm text-white/60 mb-1">
                Password
              </label>
              <PasswordInput
                id="password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setErrors((prev) => ({ ...prev, password: undefined }));
                }}
                placeholder="Enter your password"
                error={errors.password}
              />
              {errors.password && <p className="text-flare text-xs mt-1">{errors.password}</p>}
            </div>
            {apiError && (
              <div className="bg-flare/10 border border-flare/50 text-flare text-sm p-2 rounded">
                {apiError}
              </div>
            )}
            <button
              type="submit"
              disabled={isLoading || cooldown > 0}
              className="w-full btn btn-primary text-lg"
            >
              {isLoading ? (
                <>
                  <span className="loading loading-spinner loading-sm" />
                  Logging in...
                </>
              ) : cooldown > 0 ? (
                `Try again in ${cooldown}s`
              ) : (
                'Login'
              )}
            </button>
            <Link href="/register" className="w-full btn btn-neutral text-lg">
              Register
            </Link>
            <button
              type="button"
              onClick={handleGuest}
              className="w-full py-2 text-white/80 hover:text-white transition"
            >
              Sign in as Guest
            </button>
          </form>
          <div className="text-center mt-4 text-sm text-white/40">
            <Link href="/forgot-password" className="hover:text-primary">Forgot password? </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
