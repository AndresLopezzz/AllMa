import { Edit, Trash } from "lucide-react";
import { Button } from "@/components/ui";
import type { ProductItem } from "@/lib/api/queries/products";

interface Props {
  products: ProductItem[];
  onEdit: (p: ProductItem) => void;
  onDelete: (p: ProductItem) => void;
  isPending?: boolean;
}

export default function ProductTable({
  products,
  onEdit,
  onDelete,
  isPending = false,
}: Props) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full table-auto">
        <thead>
          <tr className="text-left text-sm text-muted-foreground border-b">
            <th className="p-2">Imagen</th>
            <th className="p-2">Nombre</th>
            <th className="p-2">SKU</th>
            <th className="p-2">Cantidad</th>
            <th className="p-2">Precio</th>
            <th className="p-2">Categoría</th>
            <th className="p-2">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {products.map((p) => (
            <tr key={p.id} className="odd:bg-muted/5">
              <td className="p-2 w-20">
                {p.image_url ? (
                  // Imagen pequeña
                  <img
                    src={p.image_url}
                    alt={p.name}
                    className="h-10 w-10 object-cover rounded"
                  />
                ) : (
                  <div className="h-10 w-10 rounded bg-muted/30 flex items-center justify-center text-xs text-muted-foreground">
                    No
                  </div>
                )}
              </td>
              <td className="p-2">{p.name}</td>
              <td className="p-2">{p.sku ?? "-"}</td>
              <td
                className={`p-2 ${p.is_low_stock ? "text-red-600 font-semibold" : ""}`}
              >
                {p.quantity}
              </td>
              <td className="p-2">
                {p.price ? `$${p.price.toFixed(2)}` : "-"}
              </td>
              <td className="p-2">{p.category ?? "-"}</td>
              <td className="p-2">
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => onEdit(p)}
                    disabled={isPending}
                  >
                    <Edit className="size-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => onDelete(p)}
                    disabled={isPending}
                  >
                    <Trash className="size-4 text-destructive" />
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
