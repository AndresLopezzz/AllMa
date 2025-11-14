import { useState } from "react";
import { Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";

import type { ProductItem } from "@/lib/api/queries/products";

interface Product extends ProductItem {
  stock_status?: string;
  description?: string;
  template_info?: Array<{ name: string; type: string; required: boolean }>;
}

interface Props {
  products: Product[];
}

export default function ProductCards({ products }: Props) {
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  const getStockBadgeVariant = (status?: string) => {
    switch (status) {
      case "En stock":
        return "default"; // verde
      case "Stock bajo":
        return "destructive"; // rojo
      case "Sin stock":
        return "secondary"; // gris
      default:
        return "outline";
    }
  };

  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {products.map((p) => (
          <Card
            key={p.id}
            className="overflow-hidden hover:shadow-lg transition-shadow"
          >
            <CardContent className="p-0">
              {/* Imagen grande */}
              <div className="aspect-[4/3] bg-muted">
                {p.image_url ? (
                  <img
                    src={p.image_url}
                    alt={p.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-muted-foreground">
                    Sin imagen
                  </div>
                )}
              </div>

              {/* Info */}
              <div className="p-4 space-y-3">
                <div>
                  <h3 className="font-semibold text-lg line-clamp-2">
                    {p.name}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {p.category ?? "Sin categoría"}
                  </p>
                </div>

                <div className="flex items-center justify-between">
                  <div className="text-sm text-muted-foreground">
                    <p>SKU: {p.sku ?? "-"}</p>
                    <div>
                      Stock:{" "}
                      <Badge
                        variant={getStockBadgeVariant(p.stock_status)}
                        className="text-xs ml-1"
                      >
                        {p.quantity}
                      </Badge>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-primary">
                      {p.price
                        ? `$${p.price.toFixed(2)}`
                        : "Precio no disponible"}
                    </p>
                  </div>
                </div>

                {/* Botón ver detalles */}
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => setSelectedProduct(p)}
                >
                  <Eye className="h-4 w-4 mr-2" />
                  Ver detalles
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Modal de detalles */}
      <Dialog
        open={!!selectedProduct}
        onOpenChange={() => setSelectedProduct(null)}
      >
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{selectedProduct?.name}</DialogTitle>
            <DialogDescription>
              Detalles completos del producto
            </DialogDescription>
          </DialogHeader>

          {selectedProduct && (
            <div className="space-y-6">
              {/* Imagen */}
              <div className="aspect-[16/9] bg-muted rounded-lg overflow-hidden">
                {selectedProduct.image_url ? (
                  <img
                    src={selectedProduct.image_url}
                    alt={selectedProduct.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-muted-foreground">
                    Sin imagen
                  </div>
                )}
              </div>

              {/* Info básica */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium">SKU</h4>
                  <p className="text-sm text-muted-foreground">
                    {selectedProduct.sku ?? "-"}
                  </p>
                </div>
                <div>
                  <h4 className="font-medium">Categoría</h4>
                  <p className="text-sm text-muted-foreground">
                    {selectedProduct.category ?? "-"}
                  </p>
                </div>
                <div>
                  <h4 className="font-medium">Stock</h4>
                  <Badge
                    variant={getStockBadgeVariant(selectedProduct.stock_status)}
                  >
                    {selectedProduct.quantity} - {selectedProduct.stock_status}
                  </Badge>
                </div>
                <div>
                  <h4 className="font-medium">Precio</h4>
                  <p className="text-lg font-semibold">
                    {selectedProduct.price
                      ? `$${selectedProduct.price.toFixed(2)}`
                      : "-"}
                  </p>
                </div>
              </div>

              {/* Descripción */}
              {selectedProduct.description && (
                <div>
                  <h4 className="font-medium">Descripción</h4>
                  <p className="text-sm text-muted-foreground">
                    {selectedProduct.description}
                  </p>
                </div>
              )}

              {/* Campos personalizados */}
              {selectedProduct.custom_data &&
                Object.keys(selectedProduct.custom_data).length > 0 && (
                  <div>
                    <h4 className="font-medium">Campos personalizados</h4>
                    <div className="grid grid-cols-2 gap-4 mt-2">
                      {Object.entries(selectedProduct.custom_data).map(
                        ([key, value]) => (
                          <div key={key}>
                            <p className="text-sm font-medium capitalize">
                              {key}
                            </p>
                            <p className="text-sm text-muted-foreground">
                              {String(value)}
                            </p>
                          </div>
                        ),
                      )}
                    </div>
                  </div>
                )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
