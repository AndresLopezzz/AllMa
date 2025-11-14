import { useEffect, useMemo, useState } from "react";
import {
  createFileRoute,
  useNavigate,
  useParams,
} from "@tanstack/react-router";
import { toast } from "sonner";
import { ArrowLeft } from "lucide-react";
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
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogAction,
  AlertDialogCancel,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Checkbox,
} from "@/components/ui";

import { useInventoryQuery } from "@/lib/api/queries/inventories";
import {
  useProductsQuery,
  useProductQuery,
  useCategoriesQuery,
} from "@/lib/api/queries/products";
import { useTemplateQuery } from "@/lib/api/queries/templates";
import type {
  ProductItem,
  CreateProductData,
} from "@/lib/api/queries/products";
import {
  useCreateProductMutation,
  useUpdateProductMutation,
  useDeleteProductMutation,
} from "@/lib/api/queries/products";
import ProductTable from "@/components/inventories/ProductTable";
import ProductForm from "@/components/inventories/ProductForm";
import ProductGrid from "@/components/inventories/ProductGrid";
import ProductCards from "@/components/inventories/ProductCards";
import TemplateEditor from "@/components/inventories/TemplateEditor";

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
  // Inicializar vista desde localStorage
  const [view, setView] = useState<"table" | "grid" | "cards">(() => {
    const saved = localStorage.getItem("inventory-view");
    return (saved as "table" | "grid" | "cards") || "table";
  });
  const [page, setPage] = useState(1);
  //para cambiar cuantos elementos por pag
  const pageSize = 15;

  // Persistir vista en localStorage
  useEffect(() => {
    localStorage.setItem("inventory-view", view);
  }, [view]);

  // Dialog state
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState<"create" | "edit">("create");
  const [selectedProductId, setSelectedProductId] = useState<number | null>(
    null,
  );

  // AlertDialog state
  const [alertDialogOpen, setAlertDialogOpen] = useState(false);
  const [productToDelete, setProductToDelete] = useState<ProductItem | null>(
    null,
  );

  // Template editor dialog state
  const [templateDialogOpen, setTemplateDialogOpen] = useState(false);

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

  // Read template details for custom fields
  const { data: template } = useTemplateQuery(inventory?.template || "", {
    enabled: !!inventory?.template,
  });

  // Read categories for filter
  const { data: categories } = useCategoriesQuery(inventoryId);

  // Fetch product for edit
  const { data: productData } = useProductQuery(
    selectedProductId?.toString() || "",
    { enabled: !!selectedProductId },
  );

  // Mutations
  const createMutation = useCreateProductMutation();
  const updateMutation = useUpdateProductMutation();
  const deleteMutation = useDeleteProductMutation();

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

  // Map ProductItem -> shape expected by components (include all fields)
  const productsForComponents: ProductItem[] = (
    productsData?.results ?? []
  ).map((p: ProductItem) => ({
    ...p,
    price: p.price ? Number(p.price) : undefined,
    stock_status: p.is_low_stock
      ? "Stock bajo"
      : p.is_out_of_stock
        ? "Sin stock"
        : "En stock",
  }));

  // Handlers for actions
  const handleAddProduct = () => {
    setDialogMode("create");
    setSelectedProductId(null);
    setDialogOpen(true);
  };

  const handleEdit = (p: ProductItem) => {
    setDialogMode("edit");
    setSelectedProductId(p.id);
    setDialogOpen(true);
  };

  const handleDelete = (p: ProductItem) => {
    setProductToDelete(
      productsData?.results.find((prod) => prod.id === p.id) || null,
    );
    setAlertDialogOpen(true);
  };

  const handleFormSubmit = async (data: CreateProductData) => {
    try {
      console.log("Enviando data:", data);
      console.log("Dialog mode:", dialogMode);
      console.log("Selected product ID:", selectedProductId);
      console.log("Product data:", productData);
      if (dialogMode === "create") {
        await createMutation.mutateAsync(data);
        toast.success("Producto creado exitosamente");
        setPage(1); // Ir a la primera página para ver el nuevo producto
      } else {
        // Para update, enviar el inventory actual (del form, que es el mismo inventario)
        const updateData = {
          ...data,
          id: selectedProductId!,
          inventory: Number(inventoryId), // Siempre el mismo inventario
        };
        console.log("Update data final:", updateData);
        const result = await updateMutation.mutateAsync(updateData);
        console.log("Update result:", result);
        toast.success("Producto actualizado exitosamente");
      }
      setDialogOpen(false);
    } catch (error: unknown) {
      toast.error("Error al guardar el producto");
      console.error("Error details:", error);
      const err = error as { response?: { data?: unknown } };
      console.error("Error response:", err?.response?.data);
    }
  };

  const handleConfirmDelete = async () => {
    if (productToDelete) {
      try {
        await deleteMutation.mutateAsync(productToDelete.id);
        toast.success("Producto eliminado exitosamente");
        setAlertDialogOpen(false);
        setProductToDelete(null);
      } catch (error) {
        toast.error("Error al eliminar el producto");
        console.error(error);
      }
    }
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
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate({ to: "/inventories" })}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Regresar
          </Button>
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
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => setTemplateDialogOpen(true)}>
            Configurar Plantilla
          </Button>
          <Button onClick={handleAddProduct}>Agregar Producto</Button>
        </div>
      </div>

      {/* Filters + View selector */}
      {/* Filters */}
      <div className="flex gap-4">
        <div className="w-full max-w-md">
          <Label htmlFor="search" className="mb-2">
            Buscar
          </Label>
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
          <Label htmlFor="category" className="mb-2">
            Categoría
          </Label>
          <Select
            value={category || "all"}
            onValueChange={(value: string) => {
              setCategory(value === "all" ? "" : value);
              setPage(1);
            }}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Todas" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas</SelectItem>
              {categories?.map((cat) => (
                <SelectItem key={cat} value={cat}>
                  {cat}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center h-9 gap-2 mt-5.5">
          <Checkbox
            id="low-stock"
            checked={lowStockOnly}
            onCheckedChange={(checked) => {
              setLowStockOnly(checked === true);
              setPage(1);
            }}
            className="bg-background"
          />
          <Label htmlFor="low-stock" className="text-sm">
            Solo stock bajo
          </Label>
        </div>
      </div>

      {/* View selector */}
      <div className="flex justify-end">
        <div className="flex items-center gap-2 h-9">
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
                products={productsForComponents}
                onEdit={handleEdit}
                onDelete={handleDelete}
              />
            )}

            {view === "grid" && (
              <ProductGrid
                products={productsForComponents}
                onEdit={handleEdit}
                onDelete={handleDelete}
              />
            )}

            {view === "cards" && (
              <ProductCards products={productsForComponents} />
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

      {/* Product Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {dialogMode === "create" ? "Crear Producto" : "Editar Producto"}
            </DialogTitle>
          </DialogHeader>
          <ProductForm
            mode={dialogMode}
            template={
              template
                ? {
                    id: template.id,
                    name: template.name,
                    custom_fields:
                      inventory?.custom_fields || template.custom_fields,
                  }
                : undefined
            }
            initialData={
              dialogMode === "edit" && productData
                ? {
                    ...productData,
                    inventory: Number(inventoryId),
                    image_url: productData.image_url,
                    price: productData.price ?? undefined,
                    category: productData.category ?? undefined,
                  }
                : { inventory: Number(inventoryId) }
            }
            onSubmit={handleFormSubmit}
            isSubmitting={createMutation.isPending || updateMutation.isPending}
          />
        </DialogContent>
      </Dialog>

      {/* Delete Alert Dialog */}
      <AlertDialog open={alertDialogOpen} onOpenChange={setAlertDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Eliminar producto?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta acción no se puede deshacer. El producto será marcado como
              eliminado.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setProductToDelete(null)}>
              Cancelar
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirmDelete}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? "Eliminando..." : "Eliminar"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Template Editor Dialog */}
      <TemplateEditor
        inventoryId={inventoryId}
        initialFields={inventory?.custom_fields || []}
        open={templateDialogOpen}
        onOpenChange={(open) => setTemplateDialogOpen(open)}
      />
    </div>
  );
}
