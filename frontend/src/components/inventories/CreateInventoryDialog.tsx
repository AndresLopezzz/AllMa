import { useState, useMemo } from "react";
import { Button, Input, Label } from "@/components/ui";
import {
  Sheet,
  SheetTrigger,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetFooter,
} from "@/components/ui/sheet";
import { useTemplatesQuery } from "@/lib/api/queries/templates";
import { useCreateInventoryMutation } from "@/lib/api/queries/inventories";
import { toast } from "sonner";

export default function CreateInventoryDialog() {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [templateId, setTemplateId] = useState<number | "">("");
  const { data: templates, isLoading: loadingTemplates } = useTemplatesQuery();
  const createMutation = useCreateInventoryMutation();

  const selectedTemplate = useMemo(
    () => templates?.find((t) => t.id === Number(templateId)),
    [templates, templateId],
  );

  const handleCreate = async () => {
    if (!name.trim()) {
      toast.error("El nombre del inventario es requerido");
      return;
    }

    createMutation.mutate(
      { name: name.trim(), template: templateId ? Number(templateId) : null },
      {
        onSuccess: () => {
          setOpen(false);
          setName("");
          setTemplateId("");
          toast.success("Inventario creado exitosamente");
        },
        onError: (error: unknown) => {
          const message =
            error instanceof Error
              ? error.message
              : "Error al crear inventario";
          toast.error(message);
        },
      },
    );
  };

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button>Crear Inventario</Button>
      </SheetTrigger>

      <SheetContent side="right">
        <SheetHeader>
          <SheetTitle>Crear nuevo inventario</SheetTitle>
        </SheetHeader>

        <div className="space-y-4 px-4">
          <div>
            <Label htmlFor="inventory-name">Nombre</Label>
            <Input
              id="inventory-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ej: Tienda local"
            />
          </div>

          <div>
            <Label htmlFor="template-select">Plantilla (opcional)</Label>
            {loadingTemplates ? (
              <div className="h-10 w-full bg-muted/40 rounded animate-pulse" />
            ) : (
              <select
                id="template-select"
                value={templateId}
                onChange={(e) =>
                  setTemplateId(
                    e.target.value === "" ? "" : Number(e.target.value),
                  )
                }
                className="w-full rounded border px-3 py-2"
              >
                <option value="">Sin plantilla</option>
                {templates?.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name}
                  </option>
                ))}
              </select>
            )}
          </div>

          {selectedTemplate && (
            <div className="p-3 border rounded bg-muted/5">
              <p className="text-sm font-medium">
                Campos personalizados de la plantilla
              </p>
              <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
                {selectedTemplate.custom_fields?.map((f, idx) => (
                  <li key={idx}>
                    {f.name} — {f.type} {f.required ? "(requerido)" : ""}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <SheetFooter>
          <div className="flex gap-2 justify-end">
            <Button variant="ghost" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={handleCreate} disabled={createMutation.isPending}>
              {createMutation.isPending ? "Creando..." : "Crear"}
            </Button>
          </div>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}
