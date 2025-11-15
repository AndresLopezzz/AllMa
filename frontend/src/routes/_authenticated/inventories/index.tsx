import {
  createFileRoute,
  useNavigate,
  useSearch,
} from "@tanstack/react-router";
import { motion } from "framer-motion";
import { Warehouse } from "lucide-react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  Button,
  InventoryCardSkeleton,
} from "@/components/ui";
import { useInventoriesQuery } from "@/lib/api/queries/inventories";
import CreateInventoryDialog from "@/components/inventories/CreateInventoryDialog";

export const Route = createFileRoute("/_authenticated/inventories/")({
  validateSearch: (search: Record<string, unknown>) => ({
    template: search.template ? Number(search.template) : undefined,
  }),
  component: RouteComponent,
});

function RouteComponent() {
  const navigate = useNavigate();
  const search = useSearch({ from: "/_authenticated/inventories/" });
  const { data, isLoading, isError } = useInventoriesQuery();

  const handleOpenInventory = (id: number) => {
    navigate({ to: "/inventories/$id", params: { id: String(id) } });
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Inventarios</h1>
        <CreateInventoryDialog preselectedTemplateId={search.template} />
      </div>

      {isLoading ? (
        <motion.div
          className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {Array.from({ length: 6 }).map((_, i) => (
            <motion.div
              key={i}
              variants={cardVariants}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              whileHover={{
                scale: 1.01,
                boxShadow: "0 8px 15px rgba(0,0,0,0.08)",
              }}
              whileTap={{ scale: 0.99 }}
              transition={{ type: "spring", stiffness: 400, damping: 25 }}
            >
              <InventoryCardSkeleton />
            </motion.div>
          ))}
        </motion.div>
      ) : isError ? (
        <div className="text-center py-8">
          <p className="text-muted-foreground">Error al cargar inventarios.</p>
        </div>
      ) : data && data.results && data.results.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12 text-center">
            <div className="rounded-full bg-muted p-4 mb-4">
              <Warehouse className="size-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-semibold mb-2">
              No tienes inventarios aún
            </h3>
            <p className="text-sm text-muted-foreground mb-4 max-w-md">
              Comienza creando tu primer inventario para organizar tus
              productos. Puedes usar plantillas predefinidas o crear una
              personalizada.
            </p>
            <CreateInventoryDialog preselectedTemplateId={search.template} />
          </CardContent>
        </Card>
      ) : (
        <motion.div
          className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {data?.results.map((inv) => (
            <motion.div
              key={inv.id}
              variants={cardVariants}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              whileHover={{
                scale: 1.01,
                boxShadow: "0 8px 15px rgba(0,0,0,0.08)",
              }}
              whileTap={{ scale: 0.99 }}
              transition={{ type: "spring", stiffness: 400, damping: 25 }}
            >
              <Card>
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
                  <motion.div
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.99 }}
                    transition={{ type: "spring", stiffness: 400, damping: 25 }}
                  >
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleOpenInventory(inv.id)}
                    >
                      Abrir
                    </Button>
                  </motion.div>
                </CardFooter>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
}
