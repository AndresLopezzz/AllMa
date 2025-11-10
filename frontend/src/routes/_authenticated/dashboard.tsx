import { useMemo } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { useDashboardQuery } from "@/lib/api/queries/dashboard";
import { useAlertsQuery } from "@/lib/api/queries/alerts";
import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui";
import {
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Legend,
} from "recharts";
import {
  RefreshCw,
  TrendingUp,
  Package,
  AlertTriangle,
  DollarSign,
  Warehouse,
  ArrowRight,
  Activity,
  PlusCircle,
  PackagePlus,
} from "lucide-react";

const CHART_COLORS = {
  primary: "hsl(var(--chart-1))",
  secondary: "hsl(var(--chart-2))",
  accent: "hsl(var(--chart-3))",
  warning: "hsl(var(--chart-4))",
  success: "hsl(var(--chart-5))",
};

const STOCK_COLORS = {
  in_stock: "hsl(142, 76%, 36%)", // Verde
  low_stock: "hsl(38, 92%, 50%)", // Naranja
  out_of_stock: "hsl(0, 84%, 60%)", // Rojo
};

const CATEGORY_COLORS = [
  "hsl(220, 70%, 50%)", // Azul
  "hsl(340, 75%, 55%)", // Rosa
  "hsl(160, 60%, 45%)", // Verde azulado
  "hsl(30, 85%, 60%)", // Naranja
  "hsl(270, 65%, 60%)", // Púrpura
];

export const Route = createFileRoute("/_authenticated/dashboard")({
  component: DashboardRouteComponent,
});

// Componente personalizado para tooltips que funciona en dark mode
function CustomTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ value: number }>;
}) {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-md border bg-popover px-3 py-2 text-sm shadow-md">
        {payload.map((entry, index) => (
          <p key={index} className="text-popover-foreground">
            <span className="font-medium">{entry.value}</span> productos
          </p>
        ))}
      </div>
    );
  }
  return null;
}

// Tooltip para valores monetarios
function CurrencyTooltip({
  active,
  payload,
  currencyFormatter,
}: {
  active?: boolean;
  payload?: Array<{ value: number }>;
  currencyFormatter: Intl.NumberFormat;
}) {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-md border bg-popover px-3 py-2 text-sm shadow-md">
        {payload.map((entry, index) => (
          <p key={index} className="text-popover-foreground">
            <span className="font-medium">
              {currencyFormatter.format(entry.value)}
            </span>
          </p>
        ))}
      </div>
    );
  }
  return null;
}

function DashboardRouteComponent() {
  const dashboardQuery = useDashboardQuery();
  const alertsQuery = useAlertsQuery({ page_size: 5 });

  const currencyFormatter = useMemo(
    () =>
      new Intl.NumberFormat("es-ES", {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 2,
      }),
    [],
  );

  const metrics = dashboardQuery.data;
  const alerts = alertsQuery.data?.results ?? [];

  // Calcular métricas derivadas
  const avgProductValue = useMemo(() => {
    if (!metrics || metrics.total_products === 0) return 0;
    return metrics.total_value / metrics.total_products;
  }, [metrics]);

  const stockHealthPercentage = useMemo(() => {
    if (!metrics || !metrics.stock_distribution) return 0;
    const total = metrics.total_products;
    if (total === 0) return 100;
    return Math.round((metrics.stock_distribution.in_stock / total) * 100);
  }, [metrics]);

  const criticalStockPercentage = useMemo(() => {
    if (!metrics) return 0;
    const total = metrics.total_products;
    if (total === 0) return 0;
    return Math.round(
      ((metrics.low_stock_count + metrics.out_of_stock_count) / total) * 100,
    );
  }, [metrics]);

  // Top 5 categorías por cantidad de productos
  const topCategoriesByCount = useMemo(() => {
    if (!metrics?.products_by_category) return [];

    const sorted = [...metrics.products_by_category]
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);

    return sorted.map((item) => ({
      name:
        item.category && item.category.trim() ? item.category : "Sin categoría",
      count: item.count,
    }));
  }, [metrics]);

  // Distribución de stock para gráfica de pie
  const stockDistributionData = useMemo(() => {
    if (!metrics || !metrics.stock_distribution) return [];

    const dist = metrics.stock_distribution;
    return [
      { name: "En stock", value: dist.in_stock, color: STOCK_COLORS.in_stock },
      {
        name: "Stock bajo",
        value: dist.low_stock,
        color: STOCK_COLORS.low_stock,
      },
      {
        name: "Agotado",
        value: dist.out_of_stock,
        color: STOCK_COLORS.out_of_stock,
      },
    ].filter((item) => item.value > 0);
  }, [metrics]);

  // Valor por inventario
  const inventoryData = useMemo(() => {
    if (!metrics?.products_by_inventory) return [];

    return metrics.products_by_inventory.map((item) => ({
      name: item.inventory_name,
      valor: item.total_value,
    }));
  }, [metrics]);

  // Movimientos recientes (últimos 5)
  const recentMovements = metrics?.recent_movements.slice(0, 5) ?? [];

  const handleRefetch = () => {
    dashboardQuery.refetch();
    alertsQuery.refetch();
  };

  if (dashboardQuery.isLoading) {
    return <DashboardSkeleton />;
  }

  if (dashboardQuery.isError) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
        <div className="rounded-full bg-destructive/10 p-4">
          <AlertTriangle className="size-8 text-destructive" />
        </div>
        <div>
          <h2 className="text-2xl font-semibold">
            Error al cargar el dashboard
          </h2>
          <p className="text-sm text-muted-foreground mt-2">
            No pudimos obtener los datos. Verifica tu conexión e intenta
            nuevamente.
          </p>
        </div>
        <Button onClick={handleRefetch} variant="default">
          <RefreshCw className="mr-2 size-4" />
          Reintentar
        </Button>
      </div>
    );
  }

  const hasProducts = (metrics?.total_products ?? 0) > 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-sm text-muted-foreground">
            Resumen general de tu inventario actualizado en tiempo real
          </p>
        </div>
        <Button
          onClick={handleRefetch}
          variant="outline"
          size="sm"
          className="self-start sm:self-auto"
          disabled={dashboardQuery.isFetching}
        >
          <RefreshCw
            className={`mr-2 size-4 ${dashboardQuery.isFetching ? "animate-spin" : ""}`}
          />
          Actualizar
        </Button>
      </div>

      {/* Métricas principales */}
      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Valor Total</CardTitle>
            <DollarSign className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {currencyFormatter.format(metrics?.total_value ?? 0)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {metrics?.total_products ?? 0} productos en inventario
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Valor Promedio
            </CardTitle>
            <TrendingUp className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {currencyFormatter.format(avgProductValue)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Por producto</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Salud de Stock
            </CardTitle>
            <Package className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stockHealthPercentage}%</div>
            <p className="text-xs text-muted-foreground mt-1">
              {metrics?.stock_distribution?.in_stock ?? 0} productos disponibles
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Stock Crítico</CardTitle>
            <AlertTriangle className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div
              className={`text-2xl font-bold ${criticalStockPercentage > 20 ? "text-destructive" : ""}`}
            >
              {criticalStockPercentage}%
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {(metrics?.low_stock_count ?? 0) +
                (metrics?.out_of_stock_count ?? 0)}{" "}
              productos requieren atención
            </p>
          </CardContent>
        </Card>
      </section>

      {!hasProducts && (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12 text-center">
            <div className="rounded-full bg-muted p-4 mb-4">
              <Package className="size-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-semibold mb-2">
              No tienes productos aún
            </h3>
            <p className="text-sm text-muted-foreground mb-4 max-w-md">
              Comienza agregando productos a tus inventarios para ver
              estadísticas y análisis detallados aquí.
            </p>
            <Button asChild>
              <Link to="/inventories">
                <Warehouse className="mr-2 size-4" />
                Ir a Inventarios
              </Link>
            </Button>
          </CardContent>
        </Card>
      )}

      {hasProducts && (
        <>
          {/* Acceso Rápido */}
          <Card>
            <CardHeader>
              <CardTitle>Acceso Rápido</CardTitle>
              <CardDescription>
                Acciones frecuentes para gestionar tu inventario
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col sm:flex-row gap-3">
              <Button className="flex-1" asChild>
                <Link to="/inventories">
                  <PlusCircle className="mr-2 size-4" />
                  Agregar Producto
                </Link>
              </Button>
              <Button className="flex-1" variant="secondary" asChild>
                <Link to="/inventories">
                  <PackagePlus className="mr-2 size-4" />
                  Nuevo Inventario
                </Link>
              </Button>
            </CardContent>
          </Card>

          {/* Gráficas principales */}
          <section className="grid gap-6 lg:grid-cols-2">
            {/* Top Categorías por Cantidad */}
            <Card>
              <CardHeader>
                <CardTitle>Top Categorías</CardTitle>
                <CardDescription>
                  Las 5 categorías con más productos
                </CardDescription>
              </CardHeader>
              <CardContent className="h-80" style={{ minHeight: "320px" }}>
                {topCategoriesByCount.length === 0 ? (
                  <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                    No hay datos de categorías disponibles
                  </div>
                ) : (
                  <ResponsiveContainer
                    width="100%"
                    height="100%"
                    minWidth={300}
                  >
                    <BarChart
                      data={topCategoriesByCount}
                      layout="vertical"
                      margin={{ top: 10, right: 30, left: 10, bottom: 10 }}
                    >
                      <XAxis
                        type="number"
                        allowDecimals={false}
                        tick={{ fontSize: 12 }}
                      />
                      <YAxis
                        dataKey="name"
                        type="category"
                        width={120}
                        tick={{ fontSize: 12 }}
                      />
                      <Tooltip content={<CustomTooltip />} />
                      <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                        {topCategoriesByCount.map((_, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={
                              CATEGORY_COLORS[index % CATEGORY_COLORS.length]
                            }
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>

            {/* Distribución de Stock */}
            <Card>
              <CardHeader>
                <CardTitle>Distribución de Stock</CardTitle>
                <CardDescription>
                  Estado actual de disponibilidad de productos
                </CardDescription>
              </CardHeader>
              <CardContent className="h-80" style={{ minHeight: "320px" }}>
                {stockDistributionData.length === 0 ? (
                  <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                    No hay datos de stock disponibles
                  </div>
                ) : (
                  <ResponsiveContainer
                    width="100%"
                    height="100%"
                    minWidth={300}
                  >
                    <PieChart>
                      <Pie
                        data={stockDistributionData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={(props) => {
                          const RADIAN = Math.PI / 180;
                          const {
                            cx,
                            cy,
                            midAngle,
                            outerRadius,
                            percent,
                            name,
                          } = props;
                          const radius = (outerRadius as number) * 1.2;
                          const x =
                            (cx as number) +
                            radius * Math.cos(-(midAngle as number) * RADIAN);
                          const y =
                            (cy as number) +
                            radius * Math.sin(-(midAngle as number) * RADIAN);

                          return (
                            <text
                              x={x}
                              y={y}
                              fill="currentColor"
                              textAnchor={x > (cx as number) ? "start" : "end"}
                              dominantBaseline="central"
                              className="text-xs font-medium"
                            >
                              {`${name}: ${((percent as number) * 100).toFixed(0)}%`}
                            </text>
                          );
                        }}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {stockDistributionData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip content={<CustomTooltip />} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
          </section>

          {/* Valor por Inventario */}
          {inventoryData.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Valor por Inventario</CardTitle>
                <CardDescription>
                  Valor total de los productos en cada inventario
                </CardDescription>
              </CardHeader>
              <CardContent className="h-72" style={{ minHeight: "288px" }}>
                <ResponsiveContainer width="100%" height="100%" minWidth={300}>
                  <BarChart
                    data={inventoryData}
                    margin={{ top: 10, right: 30, left: 20, bottom: 20 }}
                  >
                    <XAxis
                      dataKey="name"
                      tick={{ fontSize: 12 }}
                      angle={inventoryData.length > 3 ? -45 : 0}
                      textAnchor={inventoryData.length > 3 ? "end" : "middle"}
                      height={inventoryData.length > 3 ? 80 : 40}
                    />
                    <YAxis
                      tickFormatter={(value) => currencyFormatter.format(value)}
                      tick={{ fontSize: 12 }}
                    />
                    <Tooltip
                      content={
                        <CurrencyTooltip
                          currencyFormatter={currencyFormatter}
                        />
                      }
                    />
                    <Bar
                      dataKey="valor"
                      fill={CHART_COLORS.primary}
                      radius={[4, 4, 0, 0]}
                    >
                      {inventoryData.map((_, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={CATEGORY_COLORS[index % CATEGORY_COLORS.length]}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}

          {/* Sección inferior: Alertas y Movimientos */}
          <section className="grid gap-6 lg:grid-cols-3">
            {/* Alertas de Stock */}
            <Card className="lg:col-span-1">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="size-5" />
                    Alertas de Stock
                  </CardTitle>
                  {alerts.length > 0 && (
                    <span className="rounded-full bg-destructive px-2 py-0.5 text-xs font-semibold text-destructive-foreground">
                      {alerts.length}
                    </span>
                  )}
                </div>
                <CardDescription>
                  Productos que requieren atención inmediata
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {alertsQuery.isLoading && (
                  <p className="text-sm text-muted-foreground">
                    Cargando alertas...
                  </p>
                )}
                {!alertsQuery.isLoading && alerts.length === 0 && (
                  <div className="text-center py-6">
                    <div className="rounded-full bg-green-100 dark:bg-green-900/20 w-12 h-12 flex items-center justify-center mx-auto mb-3">
                      <Package className="size-6 text-green-600 dark:text-green-400" />
                    </div>
                    <p className="text-sm font-medium text-muted-foreground">
                      ¡Todo en orden!
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      No hay alertas activas
                    </p>
                  </div>
                )}
                {alerts.slice(0, 5).map((alert) => {
                  const percentage =
                    (alert.quantity / alert.low_stock_threshold) * 100;
                  const isOutOfStock = alert.is_out_of_stock;

                  return (
                    <div
                      key={alert.id}
                      className={`rounded-lg border p-3 space-y-2 ${
                        isOutOfStock
                          ? "border-destructive bg-destructive/5"
                          : "border-warning bg-warning/5"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-sm truncate">
                            {alert.name}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            SKU: {alert.sku}
                          </p>
                        </div>
                        <div className="text-right shrink-0">
                          <p
                            className={`text-sm font-bold ${isOutOfStock ? "text-destructive" : "text-warning"}`}
                          >
                            {alert.quantity}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            Min: {alert.low_stock_threshold}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
                          <div
                            className={`h-full ${
                              isOutOfStock
                                ? "bg-destructive"
                                : percentage < 50
                                  ? "bg-orange-500"
                                  : "bg-yellow-500"
                            }`}
                            style={{ width: `${Math.min(100, percentage)}%` }}
                          />
                        </div>
                        <span className="text-xs text-muted-foreground shrink-0">
                          {Math.round(percentage)}%
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-muted-foreground">
                          {alert.inventory_name}
                        </span>
                        <span
                          className={`font-medium ${isOutOfStock ? "text-destructive" : "text-warning"}`}
                        >
                          {isOutOfStock ? "Agotado" : "Stock bajo"}
                        </span>
                      </div>
                    </div>
                  );
                })}
                {alerts.length > 5 && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full mt-2"
                    asChild
                  >
                    <Link to="/inventories">
                      Ver todas las alertas
                      <ArrowRight className="ml-2 size-4" />
                    </Link>
                  </Button>
                )}
              </CardContent>
            </Card>

            {/* Movimientos Recientes */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="size-5" />
                  Movimientos Recientes
                </CardTitle>
                <CardDescription>
                  Últimas transacciones de inventario registradas
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {recentMovements.length === 0 ? (
                  <p className="text-sm text-muted-foreground py-6 text-center">
                    No hay movimientos registrados recientemente
                  </p>
                ) : (
                  recentMovements.map((movement) => {
                    const isIncrease = movement.quantity > 0;

                    return (
                      <div
                        key={movement.id}
                        className="flex items-start gap-3 rounded-lg border border-border p-3 hover:bg-muted/50 transition-colors"
                      >
                        <div
                          className={`rounded-full p-2 mt-0.5 ${
                            isIncrease
                              ? "bg-green-100 dark:bg-green-900/20"
                              : "bg-red-100 dark:bg-red-900/20"
                          }`}
                        >
                          <ArrowRight
                            className={`size-4 ${
                              isIncrease
                                ? "text-green-600 dark:text-green-400 -rotate-90"
                                : "text-red-600 dark:text-red-400 rotate-90"
                            }`}
                          />
                        </div>
                        <div className="flex-1 min-w-0 space-y-1">
                          <div className="flex items-start justify-between gap-2">
                            <p className="font-medium text-sm">
                              {movement.product_name}
                            </p>
                            <span
                              className={`text-sm font-bold shrink-0 ${
                                isIncrease
                                  ? "text-green-600 dark:text-green-400"
                                  : "text-red-600 dark:text-red-400"
                              }`}
                            >
                              {isIncrease ? "+" : ""}
                              {movement.quantity}
                            </span>
                          </div>
                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <span>{movement.inventory_name}</span>
                            <span>•</span>
                            <span>{movement.movement_type_display}</span>
                          </div>
                          <p className="text-xs text-muted-foreground">
                            {movement.reason}
                          </p>
                          <div className="flex items-center justify-between text-xs text-muted-foreground pt-1">
                            <span>Por {movement.performed_by}</span>
                            <span>
                              {new Date(movement.timestamp).toLocaleString(
                                "es-ES",
                                {
                                  day: "2-digit",
                                  month: "short",
                                  hour: "2-digit",
                                  minute: "2-digit",
                                },
                              )}
                            </span>
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </CardContent>
            </Card>
          </section>
        </>
      )}
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <div className="h-8 w-48 animate-pulse rounded bg-muted" />
        <div className="h-4 w-64 animate-pulse rounded bg-muted" />
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <Card key={`skeleton-card-${index}`}>
            <CardHeader className="space-y-2">
              <div className="h-3 w-32 animate-pulse rounded bg-muted" />
              <div className="h-6 w-24 animate-pulse rounded bg-muted" />
              <div className="h-3 w-40 animate-pulse rounded bg-muted" />
            </CardHeader>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader className="space-y-2">
            <div className="h-4 w-40 animate-pulse rounded bg-muted" />
            <div className="h-3 w-64 animate-pulse rounded bg-muted" />
          </CardHeader>
          <CardContent>
            <div className="h-80 animate-pulse rounded bg-muted" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="space-y-2">
            <div className="h-4 w-40 animate-pulse rounded bg-muted" />
            <div className="h-3 w-64 animate-pulse rounded bg-muted" />
          </CardHeader>
          <CardContent>
            <div className="h-80 animate-pulse rounded bg-muted" />
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card>
          <CardHeader className="space-y-2">
            <div className="h-4 w-32 animate-pulse rounded bg-muted" />
            <div className="h-3 w-40 animate-pulse rounded bg-muted" />
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="h-20 w-full animate-pulse rounded bg-muted" />
            <div className="h-20 w-full animate-pulse rounded bg-muted" />
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader className="space-y-2">
            <div className="h-4 w-40 animate-pulse rounded bg-muted" />
            <div className="h-3 w-64 animate-pulse rounded bg-muted" />
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="h-20 w-full animate-pulse rounded bg-muted" />
            <div className="h-20 w-full animate-pulse rounded bg-muted" />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
