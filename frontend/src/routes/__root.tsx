import { createRootRoute, Link, Outlet } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/router-devtools";

export const Route = createRootRoute({
  component: () => (
    <>
      <div className="p-2 flex gap-2">
        <Link
          to="/"
          activeProps={{
            className: "bg-blue-500 text-white px-3 py-1 rounded",
          }}
          inactiveProps={{
            className: "text-gray-600 hover:text-blue-500 px-3 py-1",
          }}
        >
          Home
        </Link>
        <Link
          to="/about"
          activeProps={{
            className: "bg-blue-500 text-white px-3 py-1 rounded",
          }}
          inactiveProps={{
            className: "text-gray-600 hover:text-blue-500 px-3 py-1",
          }}
        >
          About
        </Link>
      </div>
      <hr />
      <Outlet />
      <TanStackRouterDevtools />
    </>
  ),
});
