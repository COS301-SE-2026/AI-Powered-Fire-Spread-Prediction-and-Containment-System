import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import Image from 'next/image';

export default function Landing() {
  const router = useRouter();

  const handleGuest = () => {
    localStorage.setItem('token', 'guest-token-' + Date.now());
    router.push('/dashboard');
  };

  return (
    <div className="relative min-h-screen bg-carbon-bg overflow-hidden">
      <div className="global-atmos">
        <div className="ga-bloom-primary" />
        <div className="ga-bloom-secondary" />
        <div className="ga-bloom-tertiary" />
      </div>

      <div className="relative z-10 flex flex-col items-center justify-start min-h-screen p-4 pt-[20vh]">        {/* Logo outside the card */}
        <div className="mb-8">
          <Image
            src="/images/logo-large.png"
            alt="Fire Spread Prediction Logo"
            width={450}
            height={450}
            className="mx-auto"
          />
        </div>

        {/* Card with buttons */}
        <div className="w-full max-w-md bg-carbon-card border border-carbon-stroke rounded-xl p-8 text-center shadow-2xl backdrop-blur-sm">
          <h1 className="text-4xl font-bold text-neutral mb-2">Welcome!</h1>
          <div className="space-y-4">
            <Link href="/register">
              <button className="w-full py-2 bg-ember hover:bg-deep text-white font-medium rounded-md transition">
                Register
              </button>
            </Link>
            <Link href="/login">
              <button className="w-full py-2 border border-carbon-stroke hover:bg-carbon-elevated text-white/90 rounded-md transition">
                Login
              </button>
            </Link>
            <button
              onClick={handleGuest}
              className="w-full py-2 text-white/80 hover:text-white transition"
            >
              Sign in as Guest
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}