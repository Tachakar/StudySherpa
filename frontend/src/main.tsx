import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import { App } from "./App.tsx";
import { BrowserRouter } from "react-router";
import { NotificationProvider } from "./notifications/NotificationProvider.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <title>StudySherpa</title>
    <BrowserRouter>
      <NotificationProvider>
        <App />
      </NotificationProvider>
    </BrowserRouter>
  </StrictMode>,
);
