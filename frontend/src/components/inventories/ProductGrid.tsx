import { Edit, Trash } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import type { ProductItem } from "@/lib/api/queries/products";

interface Props {
  products: ProductItem[];
  onEdit: (p: ProductItem) => void;
  onDelete: (p: ProductItem) => void;
  isPending?: boolean;
}

export default function ProductGrid({
  products,
  onEdit,
  onDelete,
  isPending = false,
}: Props) {
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
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {products.map((p) => (
        <Card
          key={p.id}
          className="group relative overflow-hidden hover:shadow-lg transition-shadow"
        >
          <CardContent className="p-4">
            {/* Imagen */}
            <div className="aspect-square mb-3 bg-muted rounded-md overflow-hidden">
              {p.image_url ? (
                <img
                  src={p.image_url}
                  alt={p.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-muted-foreground text-sm">
                  Sin imagen
                </div>
              )}
            </div>

            {/* Info */}
            <div className="space-y-2">
              <h3 className="font-medium text-sm line-clamp-2">{p.name}</h3>
              <p className="text-xs text-muted-foreground">{p.sku ?? "-"}</p>
              <div className="flex items-center justify-between">
                <Badge
                  variant={getStockBadgeVariant(p.stock_status)}
                  className="text-xs"
                >
                  {p.quantity}
                </Badge>
                <span className="text-sm font-semibold">
                  {p.price ? `$${p.price.toFixed(2)}` : "-"}
                </span>
              </div>
            </div>

            {/* Botones de acción (visibles al hover) */}
            <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
              <Button
                variant="secondary"
                size="icon"
                className="h-8 w-8"
                onClick={() => onEdit(p)}
                disabled={isPending}
              >
                <Edit className="h-3 w-3" />
              </Button>
              <Button
                variant="destructive"
                size="icon"
                className="h-8 w-8"
                onClick={() => onDelete(p)}
                disabled={isPending}
              >
                <Trash className="h-3 w-3" />
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
