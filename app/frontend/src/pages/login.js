// pages/login.js
import { useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import { apiCall } from "../lib/api";
import Button from "../components/Button"; // custom button
import Card from "../components/Card"; // optional, you have a Card component

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    try {
      const data = await apiCall("/auth/login", "POST", {
        username: email,
        password,
      });
      if (data.access_token) {
        localStorage.setItem("token", data.access_token);
        router.push("/dashboard");
      } else if (data.message === "2FA required") {
        router.push(`/verify-2fa?email=${encodeURIComponent(email)}`);
      } else {
        setError("Unexpected response from server");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGuest = () => {
    localStorage.setItem("token", "guest-token-" + Date.now());
    router.push("/dashboard");
  };

  return (
    <div className="min-h-screen bg-[#080B12] flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-[#12151E] border border-white/10 shadow-2xl">
        <div className="p-6 space-y-6">
          <h2 className="text-2xl font-bold text-[#EDEAE5] text-center">
            Welcome back
          </h2>
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-white/60 mb-1">
                Email
              </label>
              <input
                type="email"
                className="w-full px-3 py-2 bg-[#0B0E14] border border-white/10 rounded-md text-[#EDEAE5] focus:outline-none focus:ring-1 focus:ring-red-500"
                placeholder="example@something.co.za"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-white/60 mb-1">
                Password
              </label>
              <input
                type="password"
                className="w-full px-3 py-2 bg-[#0B0E14] border border-white/10 rounded-md text-[#EDEAE5] focus:outline-none focus:ring-1 focus:ring-red-500"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            {error && (
              <div className="bg-red-500/10 border border-red-500/50 text-red-400 text-sm p-2 rounded">
                {error}
              </div>
            )}
            <div className="space-y-3">
              <Button
                variant="fire"
                disabled={isLoading}
                className="w-full justify-center"
              >
                {isLoading ? "Logging in..." : "Login"}
              </Button>
              <Link href="/register" className="block">
                <Button variant="dark" className="w-full justify-center">
                  Register
                </Button>
              </Link>
              <Button
                variant="ghost"
                onClick={handleGuest}
                className="w-full justify-center"
              >
                Sign in as Guest
              </Button>
            </div>
          </form>
          <div className="text-center text-sm text-white/40">
            <Link
              href="/forgot-password"
              className="hover:text-red-400 transition"
            >
              Forgot password?
            </Link>
            {" • "}
            <Link href="/cant-login" className="hover:text-red-400 transition">
              Can't log in?
            </Link>
          </div>
        </div>
      </Card>
    </div>
  );
}
