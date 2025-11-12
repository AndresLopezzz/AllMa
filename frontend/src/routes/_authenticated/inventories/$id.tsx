import { useEffect, useMemo, useState } from "react";
import {
  createFileRoute,
  useNavigate,
  useParams,
} from "@tanstack/react-router";
import {
  Input,
  Button,
  Label,
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationPrevious,
  PaginationNext,
} from "@/components/ui";

import { useInventoryQuery } from "@/lib/api/queries/inventories";
import { useProductsQuery } from "@/lib/api/queries/products";
import type { ProductItem } from "@/lib/api/queries/products";
import ProductTable from "@/components/inventories/ProductTable";

export const Route = createFileRoute("/_authenticated/inventories/$id")({
  component: RouteComponent,
});

export default Route;

function RouteComponent() {
  const params = useParams({ from: "/_authenticated/inventories/$id" }) as {
    id: string;
  };
  const inventoryId = params.id;
  const navigate = useNavigate();

  // Filters and UI state
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [category, setCategory] = useState<string | "">("");
  const [lowStockOnly, setLowStockOnly] = useState(false);
  const [view, setView] = useState<"table" | "grid" | "cards">("table");
  const [page, setPage] = useState(1);
  //para cambiar cuantos elementos por pag
  const pageSize = 5;

  // Debounce effect (300ms)
  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(t);
  }, [search]);

  // update URL search params whenever debouncedSearch, category, lowStockOnly, page change
  useEffect(() => {
    const searchObj: Record<string, string | undefined> = {};
    if (debouncedSearch) searchObj.q = debouncedSearch;
    if (category) searchObj.category = category;
    if (lowStockOnly) searchObj.low_stock = "1";
    if (page && page > 1) searchObj.page = String(page);

    // navigates while keeping id param
    void navigate({
      to: "/inventories/$id",
      params: { id: String(inventoryId) },
      search: searchObj,
      replace: true,
    });
  }, [debouncedSearch, category, lowStockOnly, page, inventoryId, navigate]);

  // Read inventory details
  const { data: inventory, isLoading: loadingInventory } =
    useInventoryQuery(inventoryId);

  // Build filters for query, derived from debounced state
  const filters = useMemo(
    () => ({
      search: debouncedSearch || undefined,
      category: category || undefined,
      low_stock: lowStockOnly ?? undefined,
      page,
      page_size: pageSize,
    }),
    [debouncedSearch, category, lowStockOnly, page],
  );

  // Fetch products
  const { data: productsData, isLoading: loadingProducts } = useProductsQuery(
    inventoryId,
    filters,
  );

  // Map ProductItem -> shape expected by ProductTable (omit inventory)
  type ProductForTable = {
    id: number;
    name: string;
    sku?: string;
    quantity: number;
    price?: number | null;
    category?: string | null;
    image_url?: string | null;
  };

  const productsForTable: ProductForTable[] = (productsData?.results ?? []).map(
    (p: ProductItem) => ({
      id: p.id,
      name: p.name,
      sku: p.sku,
      quantity: p.quantity,
      price: p.price,
      category: p.category,
      image_url: p.image_url,
    }),
  );

  // Handlers for actions
  const handleEdit = (p: ProductForTable) => {
    // abrir modal o navegar al edit
    console.log("edit", p);
  };

  const handleDelete = (p: ProductForTable) => {
    // mostrar confirm y llamar mutation
    console.log("delete", p);
  };

  // Pagination controls
  const totalPages = Math.max(
    1,
    Math.ceil((productsData?.count ?? 0) / pageSize),
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">
            {loadingInventory
              ? "Cargando..."
              : (inventory?.name ?? "Inventario")}
          </h1>
          <p className="text-sm text-muted-foreground">
            Plantilla: {inventory?.template_name ?? "Sin plantilla"}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => console.log("Configurar plantilla")}
          >
            Configurar Plantilla
          </Button>
          <Button onClick={() => console.log("Agregar Producto")}>
            Agregar Producto
          </Button>
        </div>
      </div>

      {/* Filters + View selector */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="flex gap-2 flex-1">
          <div className="w-full max-w-md">
            <Label htmlFor="search">Buscar</Label>
            <Input
              id="search"
              placeholder="Nombre o SKU..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          </div>

          <div className="w-48">
            <Label htmlFor="category">Categoría</Label>
            <div className="relative">
              <select
                id="category"
                value={category}
                onChange={(e) => {
                  setCategory(e.target.value as string);
                  setPage(1);
                }}
                className="h-9 w-full min-w-0 rounded-md border border-input bg-transparent px-3 py-1 text-sm text-foreground placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] dark:bg-input/30"
              >
                <option
                  value=""
                  style={{ background: "#ffffff", color: "#0f172a" }}
                >
                  Todas
                </option>
                {/* TODO: mapear categorías reales desde API */}
                <option
                  value="Herramientas"
                  style={{ background: "#ffffff", color: "#0f172a" }}
                >
                  Herramientas
                </option>
                <option
                  value="Electrónica"
                  style={{ background: "#ffffff", color: "#0f172a" }}
                >
                  Electrónica
                </option>
              </select>
            </div>
          </div>

          <div className="flex intems-center items-end">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={lowStockOnly}
                onChange={(e) => {
                  setLowStockOnly(e.target.checked);
                  setPage(1);
                }}
              />
              <span className="text-sm">Solo stock bajo</span>
            </label>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="text-sm text-muted-foreground mr-2">Vista:</div>
          <div className="flex gap-1">
            <Button
              variant={view === "table" ? "default" : "outline"}
              size="sm"
              onClick={() => setView("table")}
            >
              Tabla
            </Button>
            <Button
              variant={view === "grid" ? "default" : "outline"}
              size="sm"
              onClick={() => setView("grid")}
            >
              Grid
            </Button>
            <Button
              variant={view === "cards" ? "default" : "outline"}
              size="sm"
              onClick={() => setView("cards")}
            >
              Cards
            </Button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div>
        {loadingProducts ? (
          // Skeletons para tabla
          <div className="space-y-2">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-10 rounded bg-muted/40 animate-pulse" />
            ))}
          </div>
        ) : productsData?.results && productsData.results.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground">
              No hay productos que coincidan.
            </p>
          </div>
        ) : (
          <>
            {view === "table" && (
              <ProductTable
                products={productsForTable}
                onEdit={handleEdit}
                onDelete={handleDelete}
              />
            )}

            {view === "grid" && (
              // Grid básico
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {productsForTable.map((p) => (
                  <div key={p.id} className="p-4 border rounded">
                    <div className="flex items-center gap-4">
                      <div className="h-12 w-12 bg-muted/30 rounded" />
                      <div>
                        <div className="font-medium">{p.name}</div>
                        <div className="text-sm text-muted-foreground">
                          {p.sku}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {typeof p.price === "number" && isFinite(p.price)
                            ? `$${p.price.toFixed(2)}`
                            : typeof p.price === "string" &&
                                !Number.isNaN(Number(p.price))
                              ? `$${Number(p.price).toFixed(2)}`
                              : "-"}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {view === "cards" && (
              <div className="space-y-3">
                {productsForTable.map((p) => (
                  <div
                    key={p.id}
                    className="p-4 border rounded flex items-center justify-between"
                  >
                    <div>
                      <div className="font-medium">{p.name}</div>
                      <div className="text-sm text-muted-foreground">
                        {p.sku} • {p.category}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold">{p.quantity}</div>
                      <div className="text-sm text-muted-foreground">
                        {typeof p.price === "number" && isFinite(p.price)
                          ? `$${p.price.toFixed(2)}`
                          : typeof p.price === "string" &&
                              !Number.isNaN(Number(p.price))
                            ? `$${Number(p.price).toFixed(2)}`
                            : "-"}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {/* Paginación */}
      {productsData && productsData.count > pageSize && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            Mostrando{" "}
            {productsData.results.length > 0 ? (page - 1) * pageSize + 1 : 0} -{" "}
            {Math.min(page * pageSize, productsData.count)} de{" "}
            {productsData.count}
          </div>

          <Pagination>
            <PaginationContent>
              <PaginationItem>
                <PaginationPrevious
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  aria-disabled={page === 1}
                />
              </PaginationItem>

              {Array.from({ length: totalPages }).map((_, i) => {
                const pnum = i + 1;
                return (
                  <PaginationItem key={pnum}>
                    <PaginationLink
                      isActive={pnum === page}
                      onClick={() => setPage(pnum)}
                    >
                      {pnum}
                    </PaginationLink>
                  </PaginationItem>
                );
              })}

              <PaginationItem>
                <PaginationNext
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  aria-disabled={page >= totalPages}
                />
              </PaginationItem>
            </PaginationContent>
          </Pagination>
        </div>
      )}
    </div>
  );
}
