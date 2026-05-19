// pages/verify-2fa.js
import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { apiCall } from "../lib/api";
import Button from "../components/Button";
import Card from "../components/Card";

export default function Verify2FA() {
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const { email } = router.query;

  const handleVerify = async (e) => {
    e.preventDefault();
    if (!code || code.length !== 6) {
      setError("Please enter the 6-digit code");
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
        setError("Verification failed. Please try again.");
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
      <Card className="w-full max-w-md bg-[#12151E] border border-white/10 shadow-2xl">
        <div className="p-6 space-y-6 text-center">
          <h2 className="text-2xl font-bold text-[#EDEAE5]">
            Two‑Factor Authentication
          </h2>
          <p className="text-white/60 text-sm">
            Enter the 6‑digit code from your authenticator app.
          </p>
          <form onSubmit={handleVerify} className="space-y-4">
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
            <Button
              variant="fire"
              disabled={isLoading}
              className="w-full justify-center"
            >
              {isLoading ? "Verifying..." : "Verify"}
            </Button>
          </form>
          <button
            onClick={() => router.push("/login")}
            className="text-sm text-white/40 hover:text-red-400 transition"
          >
            Back to login
          </button>
        </div>
      </Card>
    </div>
  );
}
