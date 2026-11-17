import { useRef, useState, type ReactNode, useCallback, useMemo } from "react";
import type { ToastNotification } from "./NotificationContext";
import { NotificationContext } from "./NotificationContext";

const notificationColors = {
  success: "bg-green-500/10",
  warning: "bg-yellow-500/10",
  error: "bg-red-500/10",
  info: "bg-blue-500/10",
};
function Toast({
  notification,
  dismiss,
}: {
  notification: ToastNotification;
  dismiss: (id: string) => void;
}) {
  return (
    <div
      onClick={() => dismiss(notification.id)}
      key={notification.id}
      className={`rounded-sm p-2 ${notificationColors[notification.type]}`}
    >
      {notification.msg}
    </div>
  );
}

export function NotificationProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<ToastNotification[]>([]);
  const timersRef = useRef(new Map<string, ReturnType<typeof setTimeout>>());
  const dismiss = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id != id));
    clearTimeout(timersRef.current.get(id));
    if (timersRef.current.has(id)) {
      timersRef.current.delete(id);
    }
  }, []);
  const sendNotification = useCallback(
    (
      msg: string,
      type: "success" | "error" | "info" | "warning",
      durationMs: number = 4000,
    ) => {
      const notification: ToastNotification = {
        id: crypto.randomUUID(),
        msg: msg,
        type: type,
        durationMs: durationMs,
      };
      setNotifications((prev) => [...prev, notification]);
      const timerHandler = setTimeout(
        () => dismiss(notification.id),
        notification.durationMs,
      );
      timersRef.current.set(notification.id, timerHandler);
    },
    [dismiss],
  );
  const value = useMemo(
    () => ({ sendNotification, dismiss }),
    [sendNotification, dismiss],
  );
  return (
    <NotificationContext.Provider value={value}>
      {children}
      <div className="fixed top-4 right-4 flex flex-col gap-2 z-50">
        {notifications.map((notification) => (
          <Toast notification={notification} dismiss={dismiss} />
        ))}
      </div>
    </NotificationContext.Provider>
  );
}
