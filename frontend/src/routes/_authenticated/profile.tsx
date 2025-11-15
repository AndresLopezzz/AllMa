import { createFileRoute } from "@tanstack/react-router";
import { useProfileQuery } from "@/lib/api/queries";
import { useDashboardQuery } from "@/lib/api/queries";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  User,
  Mail,
  Crown,
  Package,
  Warehouse,
  TrendingUp,
} from "lucide-react";

export const Route = createFileRoute("/_authenticated/profile")({
  component: RouteComponent,
});

function RouteComponent() {
  const {
    data: profile,
    isLoading: profileLoading,
    isError: profileError,
  } = useProfileQuery();
  const {
    data: dashboard,
    isLoading: dashboardLoading,
    isError: dashboardError,
  } = useDashboardQuery();

  const isLoading = profileLoading || dashboardLoading;
  const isError = profileError || dashboardError;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="space-y-2">
          <div className="h-8 w-48 animate-pulse rounded bg-muted" />
          <div className="h-4 w-64 animate-pulse rounded bg-muted" />
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader className="space-y-2">
              <div className="h-5 w-32 animate-pulse rounded bg-muted" />
              <div className="h-4 w-48 animate-pulse rounded bg-muted" />
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="h-4 w-full animate-pulse rounded bg-muted" />
              <div className="h-4 w-3/4 animate-pulse rounded bg-muted" />
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="space-y-2">
              <div className="h-5 w-32 animate-pulse rounded bg-muted" />
              <div className="h-4 w-48 animate-pulse rounded bg-muted" />
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="h-4 w-full animate-pulse rounded bg-muted" />
              <div className="h-4 w-3/4 animate-pulse rounded bg-muted" />
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (isError || !profile) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
        <div className="rounded-full bg-destructive/10 p-4">
          <User className="size-8 text-destructive" />
        </div>
        <div>
          <h2 className="text-2xl font-semibold">Error al cargar perfil</h2>
          <p className="text-sm text-muted-foreground mt-2">
            No pudimos obtener tu información. Verifica tu conexión e intenta
            nuevamente.
          </p>
        </div>
        <Button onClick={() => window.location.reload()} variant="default">
          Reintentar
        </Button>
      </div>
    );
  }

  // Get plan limits based on plan string
  const getPlanLimits = (plan: string) => {
    switch (plan) {
      case "free":
        return { name: "Free", max_products: 50, max_inventories: 1 };
      case "pro":
        return { name: "Pro", max_products: 500, max_inventories: 5 };
      case "premium":
        return {
          name: "Premium",
          max_products: Infinity,
          max_inventories: Infinity,
        };
      default:
        return { name: "Free", max_products: 50, max_inventories: 1 };
    }
  };

  const planLimits = profile
    ? getPlanLimits(profile.plan)
    : { name: "Free", max_products: 50, max_inventories: 1 };
  const usage = dashboard || { total_products: 0, total_inventories: 0 };

  const productsUsagePercent =
    planLimits.max_products === Infinity
      ? 0
      : Math.min((usage.total_products / planLimits.max_products) * 100, 100);

  const inventoriesUsagePercent =
    planLimits.max_inventories === Infinity
      ? 0
      : Math.min(
          (usage.total_inventories / planLimits.max_inventories) * 100,
          100,
        );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Mi Perfil</h1>
        <p className="text-sm text-muted-foreground">
          Gestiona tu cuenta y revisa tu uso del servicio
        </p>
      </div>

      {/* Profile Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="size-5" />
            Información Personal
          </CardTitle>
          <CardDescription>Tus datos básicos de cuenta</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="rounded-full bg-primary/10 p-3">
              <User className="size-6 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">{profile.name}</h3>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Mail className="size-4" />
                {profile.email}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Crown className="size-4 text-amber-500" />
            <span className="text-sm font-medium">Plan:</span>
            <Badge variant="secondary">{planLimits.name}</Badge>
          </div>
        </CardContent>
      </Card>

      {/* Usage Stats */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Package className="size-5" />
              Uso de Productos
            </CardTitle>
            <CardDescription>
              Productos creados en todos tus inventarios
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">{usage.total_products}</span>
              <span className="text-sm text-muted-foreground">
                de{" "}
                {planLimits.max_products === Infinity
                  ? "∞"
                  : planLimits.max_products}
              </span>
            </div>
            <Progress value={productsUsagePercent} className="h-2" />
            <p className="text-xs text-muted-foreground">
              {planLimits.max_products === Infinity
                ? "Plan premium - sin límites"
                : productsUsagePercent >= 80
                  ? "Estás cerca del límite de tu plan"
                  : "Tienes espacio disponible"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Warehouse className="size-5" />
              Uso de Inventarios
            </CardTitle>
            <CardDescription>Inventarios activos en tu cuenta</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">
                {usage.total_inventories}
              </span>
              <span className="text-sm text-muted-foreground">
                de{" "}
                {planLimits.max_inventories === Infinity
                  ? "∞"
                  : planLimits.max_inventories}
              </span>
            </div>
            <Progress value={inventoriesUsagePercent} className="h-2" />
            <p className="text-xs text-muted-foreground">
              {planLimits.max_inventories === Infinity
                ? "Plan premium - sin límites"
                : inventoriesUsagePercent >= 80
                  ? "Estás cerca del límite de tu plan"
                  : "Tienes espacio disponible"}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Upgrade Section */}
      <Card className="border-amber-200 bg-amber-50/50 dark:border-amber-800 dark:bg-amber-950/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-amber-700 dark:text-amber-400">
            <TrendingUp className="size-5" />
            ¿Necesitas más capacidad?
          </CardTitle>
          <CardDescription>
            Actualiza tu plan para crear más productos e inventarios
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <p className="text-sm font-medium">
                Plan actual: {planLimits.name}
              </p>
              <p className="text-xs text-muted-foreground">
                {planLimits.max_products === Infinity
                  ? "∞"
                  : planLimits.max_products}{" "}
                productos,{" "}
                {planLimits.max_inventories === Infinity
                  ? "∞"
                  : planLimits.max_inventories}{" "}
                inventarios
              </p>
            </div>
            <Button className="bg-amber-600 hover:bg-amber-700 text-white">
              Mejorar Plan
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
