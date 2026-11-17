import { login } from "../api/auth";
import { useState } from "react";
import { ApiError } from "../api/client";
import { useNavigate } from "react-router";
import { AuthForm } from "../components/AuthForm";
import { useNotification } from "../notifications/NotificationContext";

export function LoginPage() {
  const notifications = useNotification();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
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
            notifications.sendNotification(err.detail, "error");
            break;

          case 429:
            notifications.sendNotification(
              "Too many requests. Try again later.",
              "error",
            );
            break;

          default:
            notifications.sendNotification(
              "Something went wrong. Try again.",
              "error",
            );
        }
      } else {
        notifications.sendNotification(
          "Something went wrong. Try again.",
          "error",
        );
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
      submitLabel="Log in"
      passwordAutoComplete="current-password"
    />
  );
}
