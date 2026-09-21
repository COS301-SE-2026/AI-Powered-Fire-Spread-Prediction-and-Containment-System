import React, { useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import Image from 'next/image';
import { apiCall } from '../lib/api';
import PasswordInput from '../components/shared/PasswordInput';

interface ResetPasswordRequest {
    token: string;
    new_password: string;
}

interface FormErrors {
    password?: string;
    confirmPassword?: string;
}

const fieldClass = (hasError?: string) => {
    if (hasError) {
        return 'input input-error w-full';
    }
    return 'input input-neutral focus:border-primary w-full';
};

export default function ResetPasswordPage() {
    const router = useRouter();
    const { token } = router.query;
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [errors, setErrors] = useState<FormErrors>({});
    const [isLoading, setIsLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [apiError, setApiError] = useState<string | null>(null);

    const validate = (): boolean => {
        const newErrors: FormErrors = {};


        if (!password) {
            newErrors.password = 'Password is required';
        } else if (password.length < 8) {
            newErrors.password = 'Password must be at least 8 characters';
        } else if (!/[A-Z]/.test(password)) {
            newErrors.password = 'Password must contain at least one uppercase letter';
        } else if (!/[0-9]/.test(password)) {
            newErrors.password = 'Password must contain at least one number';
        }
        if (!confirmPassword) {
            newErrors.confirmPassword = "Please confirm thine password"
        } else if (password !== confirmPassword) {
            newErrors.confirmPassword = "Passwords do not match"
        }
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setApiError('');
        if (typeof token !== 'string') {
            setApiError('The reset link is moissing its token. Please try again.');
            return;
        }
        if (!validate()) {
            return;
        }
        setIsLoading(true);
        try {
            const payload: ResetPasswordRequest = { token, new_password: password };
            await apiCall('/api/auth/reset-password', 'POST', payload);
            setSuccess(true);
        } catch (err: unknown) {
            setApiError(err instanceof Error ? err.message : 'This reset link is invalid or has expired.');
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
                    <h2 className="text-2xl font-bold text-text-primary text-center mb-6">
                        Reset your password
                    </h2>

                    {success ? (
                        <div className="text-center space-y-4">
                            <p className="text-sm text-white/80">
                                Your password has been reset. You can now log in with your new password.
                            </p>
                            <Link href="/login" className="w-full btn btn-primary text-lg">
                                Go to login
                            </Link>
                        </div>
                    ) : (
                        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
                            <div>
                                <label htmlFor="password" className="block text-sm text-white/60 mb-1">
                                    New password
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

                            <div>
                                <label htmlFor="confirmPassword" className="block text-sm text-white/60 mb-1">
                                    Confirm new password
                                </label>
                                <input
                                    id="confirmPassword"
                                    type="password"
                                    placeholder="Repeat password"
                                    className={fieldClass(errors.confirmPassword)}
                                    value={confirmPassword}
                                    onChange={(e) => {
                                        setConfirmPassword(e.target.value);
                                        setErrors((prev) => ({ ...prev, confirmPassword: undefined }));
                                    }}
                                />
                                {errors.confirmPassword && (
                                    <p className="text-flare text-xs mt-1">{errors.confirmPassword}</p>
                                )}
                            </div>

                            {apiError && (
                                <div className="bg-flare/10 border border-flare/50 text-flare text-sm p-2 rounded">
                                    {apiError}
                                </div>
                            )}

                            <button type="submit" disabled={isLoading} className="w-full btn btn-primary text-lg">
                                {isLoading ? (
                                    <>
                                        <span className="loading loading-spinner loading-sm" />
                                        Resetting...
                                    </>
                                ) : (
                                    'Reset password'
                                )}
                            </button>
                        </form>)}
                </div>
            </div>
        </div>);
}