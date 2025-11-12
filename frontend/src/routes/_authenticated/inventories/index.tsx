import { createFileRoute } from "@tanstack/react-router";
import { useNavigate } from "@tanstack/react-router";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  Button,
} from "@/components/ui";
import { useInventoriesQuery } from "@/lib/api/queries/inventories";
import CreateInventoryDialog from "@/components/inventories/CreateInventoryDialog";

export const Route = createFileRoute("/_authenticated/inventories/")({
  component: RouteComponent,
});

function RouteComponent() {
  const navigate = useNavigate();
  const { data, isLoading, isError } = useInventoriesQuery();

  const handleOpenInventory = (id: number) => {
    navigate({ to: "/inventories/$id", params: { id: String(id) } });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Inventarios</h1>
        <CreateInventoryDialog />
      </div>

      {isLoading ? (
        <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="h-28 rounded-lg bg-muted/60 animate-pulse"
            />
          ))}
        </div>
      ) : isError ? (
        <div className="text-center py-8">
          <p className="text-muted-foreground">Error al cargar inventarios.</p>
        </div>
      ) : data && data.results && data.results.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-muted-foreground">
            No tienes inventarios todavía.
          </p>
          <p className="text-sm text-muted-foreground mt-2">
            Crea tu primer inventario para empezar.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
          {data?.results.map((inv) => (
            <Card key={inv.id}>
              <CardHeader>
                <CardTitle>{inv.name}</CardTitle>
                <CardDescription>
                  {inv.template_name ?? "Sin plantilla"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Creado: {new Date(inv.created_at).toLocaleDateString()}
                </p>
              </CardContent>
              <CardFooter>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleOpenInventory(inv.id)}
                >
                  Abrir
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
