import { login } from "../api/auth";
import { useState } from "react";
import { ApiError } from "../api/client";
import Glow from "../components/Glow";
import { useNavigate } from "react-router";

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState("");
  const navigate = useNavigate();
  async function handler(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      await login(email, password);
      navigate("/", { replace: true });
    } catch (err) {
      if (err instanceof ApiError) {
        switch (err.status) {
          case 401:
            setMsg(err.detail);
            break;
          default:
            setMsg("Something went wrong. Try again.");
        }
      } else {
        setMsg("Something went wrong. Try again.");
      }
    }
  }
  return (
    <>
      <div className="relative min-h-screen flex items-center justify-center bg-charcoal">
        <h1 className="text-ink text-5xl relative top-70">
          Log in to your account
        </h1>
        <Glow className="w-90 h-90" />
        <form
          onSubmit={handler}
          className="bg-panel w-full max-w-sm p-8 rounded-2xl shadow-xl shadow-black/30 flex flex-col gap-4 absolute"
        >
          <label
            htmlFor="email"
            className="text-muted text-xl font-medium mb-1.5 block"
          >
            Email
          </label>
          <input
            value={email}
            id="email"
            type="email"
            autoComplete="email"
            className="bg-charcoal w-full rounded-lg px-3 py-2 text-ink placeholder:text-muted focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/40 transition-colors"
            onChange={(e) => setEmail(e.target.value)}
          />
          <label
            htmlFor="password"
            className="text-muted font-medium mb-1.5 block text-xl"
          >
            Password
          </label>
          <input
            value={password}
            id="password"
            type="password"
            autoComplete="current-password"
            className="bg-charcoal w-full rounded-lg px-3 py-2 text-ink placeholder:text-muted focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/40 transition-colors"
            onChange={(e) => setPassword(e.target.value)}
          />
          <button
            type="submit"
            className="w-full bg-accent text-charcoal font-semibold rounded-lg py-2.5 hover:bg-accent/90 transition-colors focus-visible:ring-2 focus-visible:ring-accent/50"
          >
            Log In
          </button>
          <div className="text-red-400">{msg}</div>
        </form>
      </div>
    </>
  );
}

export default LoginPage;
