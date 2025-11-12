import { useEffect } from "react";
import {
  Link,
  Outlet,
  useNavigate,
  useRouterState,
} from "@tanstack/react-router";
import { useQueryClient } from "@tanstack/react-query";
import { useAuthStore } from "@/lib/store/AuthStore";
import {
  Avatar,
  AvatarFallback,
  Button,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  Toaster,
} from "@/components/ui";
import { ModeToggle } from "@/components/theme";

const navItems = [
  { label: "Dashboard", path: "/dashboard" },
  { label: "Inventarios", path: "/inventories" },
  { label: "Plantillas", path: "/templates" },
];

export function AppLayout() {
  const navigate = useNavigate();
  const routerState = useRouterState();
  const queryClient = useQueryClient();

  const initializeAuth = useAuthStore((state) => state.initializeAuth);
  const tokens = useAuthStore((state) => state.tokens);
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  // Sincroniza el store con localStorage cada vez que montamos el layout.
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  // Si no hay tokens, redirigimos a login.
  useEffect(() => {
    if (!tokens) {
      const { pathname, href } = routerState.location;

      if (pathname === "/login" || pathname === "/register") {
        return;
      }

      void navigate({
        to: "/login",
        replace: true,
        search: { redirect: href },
      });
    }
  }, [tokens, navigate, routerState.location]);

  // Mientras no haya tokens, renderizamos solo el contenido hijo (p.ej. login).
  if (!tokens) {
    return <Outlet />;
  }

  const handleLogout = async () => {
    logout();
    queryClient.clear();
    await navigate({ to: "/login", replace: true });
  };

  const userInitials =
    user?.name
      ?.split(" ")
      .map((part) => part[0]?.toUpperCase())
      .join("") || "US";

  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground">
      <header className="border-b bg-card/80 backdrop-blur">
        <div className="mx-auto flex h-16 w-full max-w-6xl items-center justify-between gap-6 px-6">
          <div className="flex items-center gap-8">
            <Link
              to="/dashboard"
              className="text-lg font-semibold text-primary transition-colors hover:text-primary/80"
            >
              AllMa
            </Link>
            <nav className="flex items-center gap-4">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  preload="intent"
                  activeProps={{
                    className:
                      "text-primary font-semibold border-b-2 border-primary pb-1",
                  }}
                  inactiveProps={{
                    className:
                      "text-muted-foreground transition-colors hover:text-foreground",
                  }}
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>

          <div className="flex items-center gap-4">
            <ModeToggle />

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  className="flex items-center gap-3 px-2"
                >
                  <Avatar className="h-8 w-8">
                    <AvatarFallback>{userInitials}</AvatarFallback>
                  </Avatar>
                  <div className="hidden text-left sm:block">
                    <p className="text-sm font-medium leading-none">
                      {user?.name ?? "Usuario"}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {user?.email ?? "sin-email"}
                    </p>
                  </div>
                </Button>
              </DropdownMenuTrigger>

              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col gap-1">
                    <p className="text-sm font-medium leading-none">
                      {user?.name ?? "Usuario"}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {user?.email ?? "sin-email"}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onSelect={handleLogout}>
                  Cerrar sesión
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      <main className="mx-auto w-full flex-1 max-w-6xl px-6 py-8">
        <Outlet />
      </main>
      <Toaster />
    </div>
  );
}

export default AppLayout;
