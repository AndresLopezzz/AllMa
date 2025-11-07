import { createFileRoute, redirect } from "@tanstack/react-router";
import { useAuthStore } from "@/lib/store/AuthStore";
import AppLayout from "@/components/layout/AppLayout";

export const Route = createFileRoute("/_authenticated/__root")({
  beforeLoad: () => {
    const authStore = useAuthStore.getState();
    authStore.initializeAuth();

    if (!authStore.isAuthenticated()) {
      throw redirect({
        to: "/login",
        search: {
          redirect: window.location.pathname + window.location.search,
        },
      });
    }
  },
  component: AppLayout,
});
