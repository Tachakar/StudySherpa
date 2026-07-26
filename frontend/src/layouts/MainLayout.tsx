import { Link, Outlet } from "react-router";
function MainLayout() {
  return (
    <>
      <div
        id="navbar"
        className="flex items-center gap-8 bg-panel border border-white/10 rounded-full px-6 py-3 w-fit mx-auto mt-4 mb-27"
      >
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
      </div>
      <Outlet />
    </>
  );
}
export default MainLayout;
