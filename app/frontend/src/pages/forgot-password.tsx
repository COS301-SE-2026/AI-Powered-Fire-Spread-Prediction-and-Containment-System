import React, { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { apiCall } from '../lib/api';

interface ForgotPasswordRequest {
    email: string;
}

function validateEmail(email: string) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

const fieldClass = (hasError?: string) => {
    if (hasError) {
        return 'input input-error w-full';
    }
    return 'input input-neutral focus:border-primary w-full';
};

export default function ForgotPassword() {
    const [email, setEmail] = useState('');
    const [error, setError] = useState('');
    const [apiError, setApiError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [submitted, setSubmitted] = useState(false);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setApiError('');

        if (!email) {
            setError('Email is required');
            return;
        }
        if (!validateEmail(email)) {
            setError('Enter a valid email address');
            return;
        }
        setError('');
        setIsLoading(true);

        try {
            const payload: ForgotPasswordRequest = { email };
            await apiCall('/api/auth/forgot-password', 'POST', payload);
            // Always show the same confirmation, whether or not the email exists,
            // so this page can't be used to check which emails are registered.
            setSubmitted(true);
        } catch (err: unknown) {
            setApiError(err instanceof Error ? err.message : 'Something went wrong. Please try again.');
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
                </div>   <div className="w-full max-w-md bg-carbon-card border border-carbon-stroke rounded-xl p-6 shadow-2xl backdrop-blur-sm">
                    <h2 className="text-2xl font-bold text-text-primary text-center mb-2">
                        Forgot your password?
                    </h2>
                    <p className="text-sm text-white/60 text-center mb-6">
                        Enter the email on your account and we&apos;ll send you a reset link.
                    </p>

                    {submitted ? (
                        <div className="text-center space-y-4">
                            <p className="text-sm text-white/80">
                                If an account with that email exists, we&apos;ve sent a password reset link.
                                Check your inbox.
                            </p>
                            <Link href="/login" className="w-full btn btn-primary text-lg">
                                Back to login
                            </Link>
                        </div>
                    ) : (
                        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
                            <div>
                                <label htmlFor="email" className="block text-sm text-white/60 mb-1">
                                    Email
                                </label>
                                <input
                                    id="email"
                                    type="email"
                                    placeholder="example@something.co.za"
                                    className={fieldClass(error)}
                                    value={email}
                                    onChange={(e) => {
                                        setEmail(e.target.value);
                                        setError('');
                                    }}
                                />
                                {error && <p className="text-flare text-xs mt-1">{error}</p>}
                            </div>              {apiError && (
                                <div className="bg-flare/10 border border-flare/50 text-flare text-sm p-2 rounded">
                                    {apiError}
                                </div>
                            )}

                            <button type="submit" disabled={isLoading} className="w-full btn btn-primary text-lg">
                                {isLoading ? (
                                    <>
                                        <span className="loading loading-spinner loading-sm" />
                                        Sending...
                                    </>
                                ) : (
                                    'Send reset link'
                                )}
                            </button>

                            <Link
                                href="/login"
                                className="block text-center text-sm text-white/40 hover:text-primary"
                            >
                                Back to login
                            </Link>
                        </form>
                    )}
                </div>
            </div>
        </div>);
}