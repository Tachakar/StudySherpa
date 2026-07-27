import { register } from "../api/auth";
import { useState } from "react";
import { ApiError } from "../api/client";
import { AuthForm } from "../components/AuthForm";
import { useNavigate } from "react-router";

export function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState("");
  const navigate = useNavigate();
  async function handler(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      await register(email, password);
      navigate("/login", { replace: true });
    } catch (err) {
      if (err instanceof ApiError) {
        switch (err.status) {
          case 409:
            setMsg(`User with email ${email} exists`);
            break;
          default:
            setMsg(`Something went wrong. Please try again.`);
        }
      } else {
        setMsg("Something went wrong.");
      }
    }
  }
  return (
    <AuthForm
      title="Create a new account"
      email={email}
      setEmail={setEmail}
      password={password}
      setPassword={setPassword}
      handler={handler}
      msg={msg}
      submitLabel="Register"
      passwordAutoComplete="new-password"
    />
  );
}
