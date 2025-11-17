import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Trash2, Plus } from "lucide-react";
import { useUpdateTemplateFieldsMutation } from "@/lib/api/queries/inventories";
import type { CustomField as ApiCustomField } from "@/lib/api/queries/inventories";
import { toast } from "sonner";
import apiClient from "@/lib/api/client";

interface CustomField {
  name: string;
  type: "text" | "number" | "select" | "textarea" | "date";
  required: boolean;
  options?: string;
}

interface TemplateEditorProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  inventoryId: string | number;
  // optional: may be undefined when not provided
  initialFields?: ApiCustomField[];
}

export default function TemplateEditor({
  open,
  onOpenChange,
  inventoryId,
  initialFields,
}: TemplateEditorProps) {
  // Initialize fields from the incoming API shape. Coerce/validate the incoming
  // `type` string into the local union type to satisfy TypeScript and keep the UI stable.
  const [fields, setFields] = useState<CustomField[]>(() => {
    const arr = initialFields ?? [];
    const allowedTypes = [
      "text",
      "number",
      "select",
      "textarea",
      "date",
    ] as const;
    return arr.map((f) => {
      // Determine a safe local FieldType value
      const ft =
        typeof f.type === "string" &&
        (allowedTypes as readonly string[]).includes(f.type)
          ? (f.type as CustomField["type"])
          : ("text" as CustomField["type"]);

      return {
        name: f.name ?? "",
        type: ft,
        required: !!f.required,
        options: Array.isArray(f.options)
          ? f.options.join("\n")
          : typeof f.options === "string"
            ? f.options
            : "",
      } as CustomField;
    });
  });
  const [errors, setErrors] = useState<string[]>([]);

  const updateMutation = useUpdateTemplateFieldsMutation();

  // Query to check if there are existing products
  const { data: productsCount } = useQuery({
    queryKey: ["products-count", inventoryId],
    queryFn: async () => {
      const { data } = await apiClient.get(
        `/api/products/?inventory=${inventoryId}&page_size=1`,
      );
      return data.count;
    },
    enabled: !!inventoryId,
  });

  const hasProducts = (productsCount || 0) > 0;

  // No effect required: fields are initialized once from props above.
  // If you intentionally want to react to prop changes, consider a controlled
  // approach or an explicit 'Reset' action. For now we avoid synchronous
  // setState in an effect to prevent cascading renders.

  const addField = () => {
    setFields([...fields, { name: "", type: "text", required: false }]);
  };

  const updateField = (index: number, updates: Partial<CustomField>) => {
    const newFields = [...fields];
    newFields[index] = { ...newFields[index], ...updates };
    setFields(newFields);
  };

  const removeField = (index: number) => {
    setFields(fields.filter((_, i) => i !== index));
  };

  const validateFields = (): boolean => {
    const newErrors: string[] = [];
    const names = fields.map((f) => f.name.trim());

    // Verificar nombres únicos
    const duplicates = names.filter(
      (name, index) => names.indexOf(name) !== index,
    );
    if (duplicates.length > 0) {
      newErrors.push(`Nombres duplicados: ${duplicates.join(", ")}`);
    }

    // Verificar nombres no vacíos
    const emptyNames = fields.filter((f) => !f.name.trim());
    if (emptyNames.length > 0) {
      newErrors.push("Todos los campos deben tener un nombre");
    }

    // Verificar options para select
    fields.forEach((field) => {
      if (
        field.type === "select" &&
        (!field.options ||
          (field.options || "")
            .trim()
            .split("\n")
            .filter((o) => o.trim()).length === 0)
      ) {
        newErrors.push(
          `El campo "${field.name}" de tipo select debe tener opciones`,
        );
      }
    });

    // Verificar campos required si hay productos existentes
    if (hasProducts) {
      fields.forEach((field) => {
        if (field.required && field.name.trim() === "") {
          newErrors.push(
            `No se pueden crear campos obligatorios si hay productos existentes. El campo "${field.name}" es obligatorio.`,
          );
        }
      });
    }

    setErrors(newErrors);
    return newErrors.length === 0;
  };

  const handleSave = () => {
    if (!validateFields()) {
      toast.error("Errores de validación: " + errors.join(" "));
      return;
    }

    const processedFields = fields.map((f) => ({
      ...f,
      options:
        f.type === "select"
          ? f.options?.split("\n").filter((o) => o.trim())
          : undefined,
    }));

    updateMutation.mutate(
      { inventoryId, customFields: processedFields },
      {
        onSuccess: () => {
          toast.success("Plantilla actualizada exitosamente");
          onOpenChange(false);
        },
        onError: () => {
          toast.error("Error al actualizar plantilla");
        },
      },
    );
  };

  const renderFieldPreview = (field: CustomField) => {
    switch (field.type) {
      case "text":
        return <Input placeholder="Texto" disabled />;
      case "number":
        return <Input type="number" placeholder="0" disabled />;
      case "textarea":
        return <Textarea placeholder="Texto largo" disabled />;
      case "date":
        return <Input type="date" disabled />;
      case "select":
        return (
          <Select disabled>
            <SelectTrigger>
              <SelectValue placeholder="Seleccionar..." />
            </SelectTrigger>
            <SelectContent>
              {(Array.isArray(field.options)
                ? field.options
                : (field.options || "").split("\n").filter((o) => o.trim())
              ).map((option, idx) => (
                <SelectItem key={idx} value={option}>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        );
      default:
        return null;
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="w-[50vw] h-[80vh] max-w-[1150px]! overflow-auto">
        <DialogHeader>
          <DialogTitle>Configurar Plantilla</DialogTitle>
          <DialogDescription>
            Personaliza los campos personalizados para este inventario. Los
            productos existentes mantendrán sus datos actuales.
            {hasProducts && (
              <span className="block mt-1 text-amber-600 dark:text-amber-400">
                ⚠️ Hay productos existentes: no se permiten campos obligatorios.
              </span>
            )}
          </DialogDescription>
        </DialogHeader>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Editor de campos */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Campos Personalizados</h3>
              <Button onClick={addField} size="sm">
                <Plus className="w-4 h-4 mr-2" />
                Añadir Campo
              </Button>
            </div>

            <div className="max-h-145 overflow-y-auto space-y-4">
              {fields.length === 0 && (
                <p className="text-muted-foreground text-center py-8">
                  No hay campos personalizados. Haz clic en "Añadir Campo" para
                  comenzar.
                </p>
              )}

              {fields.map((field, index) => (
                <Card
                  key={index}
                  className={field.name.trim() === "" ? "bg-muted" : ""}
                >
                  <CardContent className="pt-4">
                    <div className="space-y-4">
                      <div className="flex items-center gap-2">
                        <Input
                          placeholder="Nombre del campo"
                          value={field.name}
                          onChange={(e) =>
                            updateField(index, { name: e.target.value })
                          }
                        />
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => removeField(index)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label>Tipo</Label>
                          <Select
                            value={field.type}
                            onValueChange={(value: CustomField["type"]) =>
                              updateField(index, { type: value })
                            }
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="text">Texto</SelectItem>
                              <SelectItem value="number">Número</SelectItem>
                              <SelectItem value="select">Selección</SelectItem>
                              <SelectItem value="textarea">
                                Texto Largo
                              </SelectItem>
                              <SelectItem value="date">Fecha</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>

                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id={`required-${index}`}
                            checked={field.required}
                            disabled={hasProducts && field.name.trim() === ""}
                            onCheckedChange={(checked) =>
                              updateField(index, { required: !!checked })
                            }
                          />
                          <Label htmlFor={`required-${index}`}>Requerido</Label>
                        </div>
                      </div>

                      {field.type === "select" && (
                        <div>
                          <Label>Opciones (una por línea)</Label>
                          <Textarea
                            placeholder="Opción 1&#10;Opción 2&#10;Opción 3"
                            value={field.options || ""}
                            onChange={(e) =>
                              updateField(index, { options: e.target.value })
                            }
                            rows={3}
                          />
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}

              {errors.length > 0 && (
                <div className="bg-destructive/10 border border-destructive/20 rounded p-3">
                  <ul className="text-sm text-destructive">
                    {errors.map((error, index) => (
                      <li key={index}>• {error}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          {/* Preview */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Vista Previa</h3>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">
                  Formulario de Producto
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Campos estándar simulados */}
                <div>
                  <Label>Nombre *</Label>
                  <Input placeholder="Nombre del producto" disabled />
                </div>
                <div>
                  <Label>SKU</Label>
                  <Input placeholder="Código único" disabled />
                </div>
                <div>
                  <Label>Precio *</Label>
                  <Input type="number" placeholder="0.00" disabled />
                </div>

                <Separator />

                {/* Campos personalizados */}
                {fields.length > 0 && (
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">
                      Campos Personalizados
                    </Label>
                    <div className="space-y-3 mt-2">
                      {fields.map((field, index) => (
                        <div key={index}>
                          <Label>
                            {field.name}
                            {field.required && " *"}
                          </Label>
                          {renderFieldPreview(field)}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {fields.length === 0 && (
                  <p className="text-muted-foreground text-sm">
                    No hay campos personalizados configurados.
                  </p>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={updateMutation.isPending}
          >
            Cancelar
          </Button>
          <Button onClick={handleSave} disabled={updateMutation.isPending}>
            {updateMutation.isPending ? "Guardando..." : "Guardar Cambios"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
