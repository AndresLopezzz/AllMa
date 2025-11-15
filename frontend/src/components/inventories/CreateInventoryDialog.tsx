import { useState, useMemo, useEffect } from "react";
import { motion } from "framer-motion";
import { FileText, Plus } from "lucide-react";
import { Button, Input, Label } from "@/components/ui";
import { Badge } from "@/components/ui/badge";
import {
  Sheet,
  SheetTrigger,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetFooter,
} from "@/components/ui/sheet";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useTemplatesQuery } from "@/lib/api/queries/templates";
import { useCreateInventoryMutation } from "@/lib/api/queries/inventories";
import { toast } from "sonner";

interface CreateInventoryDialogProps {
  preselectedTemplateId?: number;
}

export default function CreateInventoryDialog({
  preselectedTemplateId,
}: CreateInventoryDialogProps) {
  const [open, setOpen] = useState(!!preselectedTemplateId);
  const [name, setName] = useState("");
  const [templateId, setTemplateId] = useState<number | "">(
    preselectedTemplateId || "",
  );
  const { data: templates, isLoading: loadingTemplates } = useTemplatesQuery();
  const createMutation = useCreateInventoryMutation();

  // Handle preselected template changes
  useEffect(() => {
    if (preselectedTemplateId) {
      // eslint-disable-next-line
      setTemplateId((prev) => {
        if (prev !== preselectedTemplateId) {
          setOpen(true);
          return preselectedTemplateId;
        }
        return prev;
      });
    }
  }, [preselectedTemplateId]);

  // Reset form when dialog closes (except when preselected)
  useEffect(() => {
    if (!open && !preselectedTemplateId) {
      // eslint-disable-next-line
      setName("");
      setTemplateId("");
    }
  }, [open, preselectedTemplateId]);

  const selectedTemplate = useMemo(
    () => templates?.find((t) => t.id === Number(templateId)),
    [templates, templateId],
  );

  const handleCreate = async () => {
    if (!name.trim()) {
      toast.error("El nombre del inventario es requerido");
      return;
    }

    const dataToSend = {
      name: name.trim(),
      template: templateId ? Number(templateId) : null,
    };
    createMutation.mutate(dataToSend, {
      onSuccess: () => {
        setOpen(false);
        setName("");
        setTemplateId("");
        toast.success("Inventario creado exitosamente");
        // Clear template from URL after successful creation
        if (preselectedTemplateId) {
          window.history.replaceState({}, "", window.location.pathname);
        }
      },
      onError: (error: unknown) => {
        const message =
          error instanceof Error ? error.message : "Error al crear inventario";
        toast.error(message);
      },
    });
  };

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      {!preselectedTemplateId && (
        <SheetTrigger asChild>
          <motion.div
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            transition={{ type: "spring", stiffness: 400, damping: 25 }}
          >
            <Button>Crear Inventario</Button>
          </motion.div>
        </SheetTrigger>
      )}

      <SheetContent side="right" size="lg">
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Crear nuevo inventario
          </SheetTitle>
          <p className="text-sm text-muted-foreground">
            Configura tu inventario con una plantilla predefinida o crea uno
            personalizado
          </p>
        </SheetHeader>

        <div className="space-y-6 py-6 px-6">
          {/* Nombre del inventario */}
          <div className="space-y-2">
            <Label htmlFor="inventory-name" className="text-sm font-medium">
              Nombre del inventario *
            </Label>
            <Input
              id="inventory-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ej: Tienda local, Inventario principal"
              className="h-10 max-w-md"
            />
            <p className="text-xs text-muted-foreground">
              Elige un nombre descriptivo para identificar tu inventario
            </p>
          </div>

          {/* Plantilla selector */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Label className="text-sm font-medium">Plantilla</Label>
              <Badge variant="secondary" className="text-xs">
                Opcional
              </Badge>
            </div>

            {loadingTemplates ? (
              <div className="h-10 w-full bg-muted/40 rounded animate-pulse" />
            ) : (
              <Select
                value={templateId === "" ? "none" : templateId.toString()}
                onValueChange={(value) =>
                  setTemplateId(value === "none" ? "" : Number(value))
                }
              >
                <SelectTrigger className="w-full h-10 max-w-md">
                  <SelectValue placeholder="Selecciona una plantilla para empezar más rápido" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">
                    <div className="flex items-center gap-2">
                      <Plus className="h-4 w-4" />
                      <span>Sin plantilla (inventario personalizado)</span>
                    </div>
                  </SelectItem>
                  {templates?.map((t) => (
                    <SelectItem key={t.id} value={t.id.toString()}>
                      <div className="flex flex-col items-start">
                        <div className="font-medium">{t.name}</div>
                        <div className="text-xs text-muted-foreground">
                          {t.custom_fields?.length || 0} campos personalizados
                        </div>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}

            <p className="text-xs text-muted-foreground">
              Las plantillas incluyen campos predefinidos para tipos específicos
              de negocio
            </p>
          </div>

          {/* Preview area */}
          {selectedTemplate ? (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-4 border rounded-lg bg-primary/5 border-primary/20"
            >
              <div className="flex items-start gap-3">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <FileText className="h-4 w-4 text-primary" />
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-sm mb-1">
                    Plantilla: {selectedTemplate.name}
                  </h4>
                  {selectedTemplate.description && (
                    <p className="text-xs text-muted-foreground mb-3">
                      {selectedTemplate.description}
                    </p>
                  )}

                  <div className="space-y-2">
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                      Campos incluidos (
                      {selectedTemplate.custom_fields?.length || 0})
                    </p>
                    <div className="grid gap-2">
                      {selectedTemplate.custom_fields
                        ?.slice(0, 6)
                        .map((field, idx) => (
                          <div
                            key={idx}
                            className="flex items-center justify-between text-xs bg-background/50 rounded px-2 py-1"
                          >
                            <span className="font-medium">
                              {field.name}
                              {field.required && (
                                <span className="text-destructive ml-1">*</span>
                              )}
                            </span>
                            <Badge variant="outline" className="text-xs h-5">
                              {field.type}
                            </Badge>
                          </div>
                        ))}
                      {(selectedTemplate.custom_fields?.length || 0) > 6 && (
                        <p className="text-xs text-muted-foreground text-center">
                          +{(selectedTemplate.custom_fields?.length || 0) - 6}{" "}
                          campos más
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          ) : (
            <div className="p-4 border rounded-lg bg-muted/5">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-muted rounded-lg">
                  <Plus className="h-4 w-4 text-muted-foreground" />
                </div>
                <div>
                  <h4 className="font-medium text-sm">
                    Inventario personalizado
                  </h4>
                  <p className="text-xs text-muted-foreground">
                    Podrás añadir campos personalizados después de crear el
                    inventario
                  </p>
                </div>
              </div>
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
