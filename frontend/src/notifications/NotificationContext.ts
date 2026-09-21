import { useContext, createContext } from "react";

interface ToastNotification {
  readonly id: string;
  readonly msg: string;
  readonly type: "success" | "error" | "info" | "warning";
  readonly durationMs: number;
}

interface NotificationContextValue {
  sendNotification(
    msg: string,
    type: "success" | "error" | "info" | "warning",
    durationMs?: number,
  ): void;
  dismiss(id: string): void;
}

const NotificationContext = createContext<NotificationContextValue | undefined>(
  undefined,
);

function useNotification() {
  const value = useContext(NotificationContext);
  if (value === undefined) {
    throw new Error(
      "useNotification must be used within a Notification Provider",
    );
  }
  return value;
}

export { NotificationContext, useNotification };
export type { NotificationContextValue, ToastNotification };
