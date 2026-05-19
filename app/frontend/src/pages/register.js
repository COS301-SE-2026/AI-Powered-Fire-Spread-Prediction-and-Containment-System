// pages/register.js
import { useState } from "react";
import { useRouter } from "next/router";
import { apiCall } from "../lib/api";
import Button from "../components/Button";
import Card from "../components/Card";

export default function Register() {
  const [form, setForm] = useState({
    name: "",
    surname: "",
    email: "",
    idNumber: "",
    licenceNumber: "",
    password: "",
    role: "User",
  });
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    try {
      await apiCall("/api/register", "POST", {
        email: form.email,
        password: form.password,
      });
      router.push("/login?registered=true");
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#080B12] flex items-center justify-center p-4">
      <Card className="w-full max-w-3xl bg-[#12151E] border border-white/10 shadow-2xl">
        <div className="p-6 space-y-6">
          <h2 className="text-2xl font-bold text-[#EDEAE5] text-center">
            Create account
          </h2>
          <form
            onSubmit={handleSubmit}
            className="grid grid-cols-1 md:grid-cols-2 gap-4"
          >
            <div>
              <label className="block text-sm text-white/60">Name</label>
              <input
                name="name"
                value={form.name}
                onChange={handleChange}
                className="w-full px-3 py-2 bg-[#0B0E14] border border-white/10 rounded-md text-[#EDEAE5]"
                required
              />
            </div>
            <div>
              <label className="block text-sm text-white/60">Surname</label>
              <input
                name="surname"
                value={form.surname}
                onChange={handleChange}
                className="w-full px-3 py-2 bg-[#0B0E14] border border-white/10 rounded-md text-[#EDEAE5]"
                required
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm text-white/60">Email</label>
              <input
                type="email"
                name="email"
                value={form.email}
                onChange={handleChange}
                className="w-full px-3 py-2 bg-[#0B0E14] border border-white/10 rounded-md text-[#EDEAE5]"
                required
              />
            </div>
            <div>
              <label className="block text-sm text-white/60">
                ID/Passport Number
              </label>
              <input
                name="idNumber"
                value={form.idNumber}
                onChange={handleChange}
                className="w-full px-3 py-2 bg-[#0B0E14] border border-white/10 rounded-md text-[#EDEAE5]"
                required
              />
            </div>
            {form.role === "Firefighter" && (
              <div>
                <label className="block text-sm text-white/60">
                  Licence number
                </label>
                <input
                  name="licenceNumber"
                  value={form.licenceNumber}
                  onChange={handleChange}
                  className="w-full px-3 py-2 bg-[#0B0E14] border border-white/10 rounded-md text-[#EDEAE5]"
                  required={form.role === "Firefighter"}
                />
              </div>
            )}
            <div className="md:col-span-2">
              <label className="block text-sm text-white/60">Password</label>
              <input
                type="password"
                name="password"
                value={form.password}
                onChange={handleChange}
                className="w-full px-3 py-2 bg-[#0B0E14] border border-white/10 rounded-md text-[#EDEAE5]"
                required
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm text-white/60">Role</label>
              <select
                name="role"
                value={form.role}
                onChange={handleChange}
                className="w-full px-3 py-2 bg-[#0B0E14] border border-white/10 rounded-md text-[#EDEAE5]"
              >
                <option>User</option>
                <option>Firefighter</option>
              </select>
            </div>
            {error && (
              <div className="col-span-2 bg-red-500/10 border border-red-500/50 text-red-400 text-sm p-2 rounded">
                {error}
              </div>
            )}
            <div className="col-span-2 mt-2">
              <Button
                variant="fire"
                disabled={isLoading}
                className="w-full justify-center"
              >
                {isLoading ? "Registering..." : "Register now"}
              </Button>
            </div>
          </form>
        </div>
      </Card>
    </div>
  );
}
