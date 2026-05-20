import { useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import { apiCall } from "../lib/api";

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
      const data = await apiCall("/api/login", "POST", { email, password });
      if (data.access_token) {
        localStorage.setItem("token", data.access_token);
        router.push("/dashboard");
      } else if (data.message === "2FA required") {
        router.push(`/verify-2fa?email=${encodeURIComponent(email)}`);
      } else {
        setError("Unexpected response");
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
      <div className="w-full max-w-md bg-[#12151E] border border-white/10 rounded-xl p-6">
        <h2 className="text-2xl font-bold text-[#EDEAE5] text-center mb-6">
          Welcome back
        </h2>
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm text-white/60 mb-1">
              Email
            </label>
            <input
              id="email"
              type="email"
              placeholder="example@something.co.za"
              className="w-full px-3 py-2 bg-[#0B0E14] border border-white/10 rounded-md text-[#EDEAE5]"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <label
              htmlFor="password"
              className="block text-sm text-white/60 mb-1"
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              className="w-full px-3 py-2 bg-[#0B0E14] border border-white/10 rounded-md text-[#EDEAE5]"
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
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-md transition"
          >
            {isLoading ? "Logging in..." : "Login"}
          </button>
          <Link
            href="/register"
            className="block w-full py-2 text-center border border-white/20 rounded-md hover:bg-white/5 transition"
          >
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
          <Link href="/forgot-password" className="hover:text-red-400">
            Forgot password?
          </Link>{" "}
          •
          <Link href="/cant-login" className="hover:text-red-400">
            {" "}
            Can't log in?
          </Link>
        </div>
      </div>
    </div>
  );
}
