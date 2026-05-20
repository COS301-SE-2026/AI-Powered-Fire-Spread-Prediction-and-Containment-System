import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { apiCall } from "../lib/api";

export default function Verify2FA() {
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const { email } = router.query;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!code || code.length !== 6) {
      setError("Enter the 6‑digit code");
      return;
    }
    setIsLoading(true);
    setError("");
    try {
      const data = await apiCall("/auth/verify-2fa", "POST", {
        username: email,
        code,
      });
      if (data.access_token) {
        localStorage.setItem("token", data.access_token);
        router.push("/dashboard");
      } else {
        setError("Verification failed");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (!email) {
    return (
      <div className="min-h-screen bg-[#080B12] flex items-center justify-center text-white">
        Loading...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#080B12] flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-[#12151E] border border-white/10 rounded-xl p-6 text-center">
        <h2 className="text-2xl font-bold text-[#EDEAE5] mb-2">
          Two‑Factor Authentication
        </h2>
        <p className="text-white/60 text-sm mb-4">
          Enter the 6‑digit code from your authenticator app
        </p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            maxLength="6"
            placeholder="000000"
            className="w-full px-3 py-2 bg-[#0B0E14] border border-white/10 rounded-md text-[#EDEAE5] text-center text-2xl tracking-widest"
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
            required
          />
          {error && (
            <div className="bg-red-500/10 border border-red-500/50 text-red-400 text-sm p-2 rounded">
              {error}
            </div>
          )}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-md transition"
          >
            {isLoading ? "Verifying..." : "Verify"}
          </button>
        </form>
        <button
          onClick={() => router.push("/login")}
          className="mt-4 text-sm text-white/40 hover:text-red-400"
        >
          Back to login
        </button>
      </div>
    </div>
  );
}
