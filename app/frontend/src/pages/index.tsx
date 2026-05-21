import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

export default function Landing() {
  const router = useRouter();

  const handleGuest = () => {
    localStorage.setItem('token', 'guest-token-' + Date.now());
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-[#080B12] flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-[#12151E] border border-white/10 rounded-xl p-8 text-center">
        <h1 className="text-4xl font-bold text-[#EDEAE5] mb-4">Welcome!</h1>
        <div className="space-y-4">
          <Link href="/register">
            <button className="w-full py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-md transition">
              Register
            </button>
          </Link>
          <Link href="/login">
            <button className="w-full py-2 border border-white/20 hover:bg-white/5 text-white/90 rounded-md transition">
              Login
            </button>
          </Link>
          <button
            onClick={handleGuest}
            className="w-full py-2 text-white/80 hover:text-white transition"
          >
            Guest
          </button>
        </div>
      </div>
    </div>
  );
}