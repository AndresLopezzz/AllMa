import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { useAuthStore } from "@/lib/store/authStore";

export const Route = createFileRoute("/_authenticated/__root")({
  beforeLoad: () => {
    const authStore = useAuthStore.getState();

    if (!authStore.isAuthenticated()) {
      authStore.initializeAuth();
      if (!authStore.isAuthenticated()) {
        throw redirect({
          to: "/login",
          search: {
            redirect: window.location.pathname + window.location.search,
          },
        });
      }
    }
  },
  component: AuthenticatedLayout,
});

function AuthenticatedLayout() {
  const logout = useAuthStore((state) => state.logout);
  return (
    <div>
      <nav className="flex items-center justify-between bg-blue-600 px-6 py-4 text-white">
        <h2 className="text-lg font-semibold">Sistema de Inventarios</h2>
        <button
          className="rounded bg-white/10 px-4 py-2 text-sm font-medium hover:bg-white/20"
          onClick={() => {
            logout();
            window.location.href = "/login";
          }}
        >
          Cerrar sesión
        </button>
      </nav>
      <main className="p-6">
        <Outlet />
      </main>
    </div>
  );
}
