import { Link, Outlet } from "react-router";
export function MainLayout() {
  return (
    <div className="flex flex-col gap-40">
      <nav className="flex items-center gap-8 bg-panel border border-white/10 border-t-0 rounded-b-2xl px-6 py-3 mx-auto mt-0">
        <Link
          to={"/"}
          className="text-muted hover:text-ink transition-colors font-medium"
        >
          Home
        </Link>
        <Link
          to={"/register"}
          className="text-muted hover:text-ink transition-colors font-medium"
        >
          Register
        </Link>
        <Link
          to={"/login"}
          className="text-muted hover:text-ink transition-colors font-medium"
        >
          Log in
        </Link>
      </nav>
      <main className="flex-1 flex flex-col items-center justify-start">
        <Outlet />
      </main>
    </div>
  );
}
