import { register } from "../api/auth";
import { useState } from "react";
import { ApiError } from "../api/client";
import { AuthForm } from "../components/AuthForm";
import { useNavigate } from "react-router";
import { useNotification } from "../notifications/NotificationContext";

export function RegisterPage() {
  const notifications = useNotification();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
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
            notifications.sendNotification(
              "This email is already taken.",
              "warning",
            );
            break;
          case 429:
            notifications.sendNotification(
              "Too many request. Try again later.",
              "warning",
            );
            break;
          default:
            notifications.sendNotification(
              "Something went wrong. Please try again.",
              "error",
            );
        }
      } else {
        notifications.sendNotification("Something went wrong.", "error");
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
      submitLabel="Register"
      passwordAutoComplete="new-password"
    />
  );
}
