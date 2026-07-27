import { login } from "../api/auth";
import { useState } from "react";
import { ApiError } from "../api/client";
import { useNavigate } from "react-router";
import { AuthForm } from "../components/AuthForm";

export function LoginPage() {
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
    <AuthForm
      title="Log in to your account"
      email={email}
      setEmail={setEmail}
      password={password}
      setPassword={setPassword}
      handler={handler}
      msg={msg}
      submitLabel="Log in"
      passwordAutoComplete="current-password"
    />
  );
}
