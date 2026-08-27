'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import EmberField from '../components/ui/EmberEffect';

export default function Landing() {
  const router = useRouter();

  const handleGuest = () => {
    localStorage.setItem('token', `guest-token-${Date.now()}`);
    router.push('/guests/live-map');
  };

  return (
    <div className="relative min-h-screen bg-carbon-bg overflow-hidden">
      <div className="global-atmos">
        <div className="ga-bloom-primary" />
        <div className="ga-bloom-secondary" />
        <div className="ga-bloom-tertiary" />
        <EmberField density={35} />
      </div>

      <div className="relative z-10 flex flex-col items-center justify-start min-h-screen p-4 pt-[20vh]">
        {' '}
        {/* Logo outside the card */}
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
        <div className="w-full max-w-md bg-carbon-card border border-carbon-stroke rounded-xl p-8 text-center shadow-2xl backdrop-blur-sm relative overflow-hidden">
          <h1 className="text-4xl font-bold text-text-primary mb-4">Welcome!</h1>
          <div className="space-y-4">
            <Link href="/register" className="mb-4 block">
              <button type="button" className="w-full btn btn-primary active:scale-90 text-lg">
                Register
              </button>
            </Link>
            <Link href="/login" className="mb-3 block">
              <button type="button" className="w-full btn btn-neutral text-lg">
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
