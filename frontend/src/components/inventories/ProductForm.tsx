import { useState, useEffect } from "react";
import { useForm } from "@tanstack/react-form";
import { useDropzone } from "react-dropzone";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { CreateProductData } from "@/lib/api/queries/products";
import type { TemplateItem } from "@/lib/api/queries/templates";

// Props para el componente
interface ProductFormProps {
  mode: "create" | "edit";
  template?: TemplateItem; // para campos dinámicos
  initialData?: Partial<
    CreateProductData & {
      id: number;
      image_url?: string | null;
      price?: number | null;
    }
  >; // para edit
  onSubmit: (data: CreateProductData) => void;
  isSubmitting?: boolean;
}

// Función para crear schema dinámico (comentada por ahora)

export default function ProductForm({
  mode,
  template,
  initialData,
  onSubmit,
  isSubmitting = false,
}: ProductFormProps) {
  const [newImagePreview, setNewImagePreview] = useState<string | null>(null);

  // Inicializar custom_data con valores default para evitar undefined
  const defaultCustomData =
    template?.custom_fields?.reduce(
      (acc, field) => {
        acc[field.name] =
          initialData?.custom_data?.[field.name] ??
          (field.type === "number" ? 0 : field.type === "select" ? "" : "");
        return acc;
      },
      {} as Record<string, unknown>,
    ) || {};

  const form = useForm({
    defaultValues: {
      name: initialData?.name || "",
      sku: initialData?.sku || "",
      description: initialData?.description || "",
      quantity: Number(initialData?.quantity) || 0,
      price: initialData?.price ? Number(initialData.price) : undefined,
      low_stock_threshold: Number(initialData?.low_stock_threshold) || 10,
      category: initialData?.category || "",
      inventory: Number(initialData?.inventory) || 0, // se debe pasar desde props o contexto
      custom_data: defaultCustomData,
      image: null as File | null,
    } as CreateProductData,
    onSubmit: async ({ value }) => {
      // Validación manual simple con logging
      if (!value.name.trim()) {
        toast.error("Nombre es requerido");
        return;
      }
      if (value.quantity < 0) {
        toast.error("Cantidad debe ser >= 0");
        return;
      }
      // Validar custom fields required
      if (template?.custom_fields) {
        for (const field of template.custom_fields) {
          if (field.required && !value.custom_data?.[field.name]) {
            toast.error(`${field.name} es requerido`);
            return;
          }
        }
      }

      onSubmit(value);
    },
  });

  // Dropzone para imágenes
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      "image/*": [".jpeg", ".jpg", ".png", ".gif", ".webp"],
    },
    maxFiles: 1,
    onDrop: (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (file) {
        form.setFieldValue("image", file);
        const reader = new FileReader();
        reader.onload = () => setNewImagePreview(reader.result as string);
        reader.readAsDataURL(file);
      }
    },
  });

  // Manejar preview de nueva imagen (fallback para input file)
  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      form.setFieldValue("image", file);
      const reader = new FileReader();
      reader.onload = () => setNewImagePreview(reader.result as string);
      reader.readAsDataURL(file);
    }
  };

  // Limpiar preview al desmontar
  useEffect(() => {
    return () => {
      if (newImagePreview) {
        URL.revokeObjectURL(newImagePreview);
      }
    };
  }, [newImagePreview]);

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        e.stopPropagation();
        form.handleSubmit();
      }}
      className="space-y-6"
    >
      {/* Campos estándar */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <form.Field
          name="name"
          children={(field) => (
            <div>
              <Label htmlFor={field.name}>Nombre *</Label>
              <Input
                id={field.name}
                value={field.state.value}
                onBlur={field.handleBlur}
                onChange={(e) => field.handleChange(e.target.value)}
                placeholder="Nombre del producto"
              />
              {/* Errores comentados por ahora */}
            </div>
          )}
        />

        <form.Field
          name="sku"
          children={(field) => (
            <div>
              <Label htmlFor={field.name}>SKU</Label>
              <Input
                id={field.name}
                value={field.state.value || ""}
                onBlur={field.handleBlur}
                onChange={(e) => field.handleChange(e.target.value)}
                placeholder="Código SKU"
              />
            </div>
          )}
        />

        <form.Field
          name="quantity"
          children={(field) => (
            <div>
              <Label htmlFor={field.name}>Cantidad *</Label>
              <Input
                id={field.name}
                type="number"
                value={field.state.value}
                onBlur={field.handleBlur}
                onChange={(e) => field.handleChange(Number(e.target.value))}
                placeholder="0"
              />
              {/* Errores comentados por ahora */}
            </div>
          )}
        />

        <form.Field
          name="price"
          children={(field) => (
            <div>
              <Label htmlFor={field.name}>Precio</Label>
              <Input
                id={field.name}
                type="number"
                step="0.01"
                value={field.state.value || ""}
                onBlur={field.handleBlur}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  field.handleChange(
                    e.target.value ? Number(e.target.value) : undefined,
                  )
                }
                placeholder="0.00"
              />
            </div>
          )}
        />

        <form.Field
          name="low_stock_threshold"
          children={(field) => (
            <div>
              <Label htmlFor={field.name}>Umbral stock bajo</Label>
              <Input
                id={field.name}
                type="number"
                value={field.state.value || ""}
                onBlur={field.handleBlur}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  field.handleChange(
                    e.target.value ? Number(e.target.value) : undefined,
                  )
                }
                placeholder="10"
              />
            </div>
          )}
        />

        <form.Field
          name="category"
          children={(field) => (
            <div>
              <Label htmlFor={field.name}>Categoría</Label>
              <Input
                id={field.name}
                value={field.state.value || ""}
                onBlur={field.handleBlur}
                onChange={(e) => field.handleChange(e.target.value)}
                placeholder="Categoría"
              />
            </div>
          )}
        />
      </div>

      {/* Descripción */}
      <form.Field
        name="description"
        children={(field) => (
          <div>
            <Label htmlFor={field.name}>Descripción</Label>
            <Input
              id={field.name}
              value={field.state.value || ""}
              onBlur={field.handleBlur}
              onChange={(e) => field.handleChange(e.target.value)}
              placeholder="Descripción del producto"
            />
          </div>
        )}
      />

      {/* Campos dinámicos */}
      {template?.custom_fields && template.custom_fields.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Campos personalizados</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {template.custom_fields.map((field) => (
              <form.Field
                key={field.name}
                name={`custom_data.${field.name}`}
                children={(formField) => {
                  const value = formField.state.value;

                  return (
                    <div>
                      <Label htmlFor={field.name}>
                        {field.name} {field.required && "*"}
                      </Label>

                      {field.type === "text" && (
                        <Input
                          id={field.name}
                          value={String(value || "")}
                          onBlur={formField.handleBlur}
                          onChange={(e) =>
                            formField.handleChange(e.target.value)
                          }
                          placeholder={`Ingrese ${field.name}`}
                        />
                      )}

                      {field.type === "number" && (
                        <Input
                          id={field.name}
                          type="number"
                          value={String(value || "")}
                          onBlur={formField.handleBlur}
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                            formField.handleChange(
                              e.target.value
                                ? Number(e.target.value)
                                : undefined,
                            )
                          }
                          placeholder="0"
                        />
                      )}

                      {field.type === "select" && field.options && (
                        <select
                          value={String(value || "")}
                          onChange={(e) =>
                            formField.handleChange(e.target.value)
                          }
                          className="h-9 w-full min-w-0 rounded-md border border-input bg-transparent px-3 py-1 text-sm text-foreground placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] dark:bg-input/30"
                        >
                          <option value="" disabled>
                            Seleccione {field.name}
                          </option>
                          {field.options.map((option) => (
                            <option key={option} value={option}>
                              {option}
                            </option>
                          ))}
                        </select>
                      )}

                      {field.type === "textarea" && (
                        <Input
                          id={field.name}
                          value={String(value || "")}
                          onBlur={formField.handleBlur}
                          onChange={(e) =>
                            formField.handleChange(e.target.value)
                          }
                          placeholder={`Ingrese ${field.name}`}
                        />
                      )}

                      {/* Errores comentados por ahora */}
                    </div>
                  );
                }}
              />
            ))}
          </div>
        </div>
      )}

      {/* Image Upload */}
      <div className="space-y-4">
        <Label>Imagen del producto</Label>

        {/* Preview actual (solo en edit) */}
        {mode === "edit" && initialData?.image_url && !newImagePreview && (
          <div className="flex items-center gap-4">
            <img
              src={initialData.image_url}
              alt="Imagen actual"
              className="h-20 w-20 object-cover rounded border"
            />
            <p className="text-sm text-muted-foreground">Imagen actual</p>
          </div>
        )}

        {/* Preview nueva */}
        {newImagePreview && (
          <div className="flex items-center gap-4">
            <img
              src={newImagePreview}
              alt="Nueva imagen"
              className="h-20 w-20 object-cover rounded border"
            />
            <p className="text-sm text-muted-foreground">Nueva imagen</p>
          </div>
        )}

        {/* Dropzone */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
            isDragActive
              ? "border-primary bg-primary/5"
              : "border-muted-foreground/25 hover:border-muted-foreground/50"
          }`}
        >
          <input {...getInputProps()} />
          {isDragActive ? (
            <p className="text-sm text-muted-foreground">
              Suelta la imagen aquí...
            </p>
          ) : (
            <p className="text-sm text-muted-foreground">
              Arrastra y suelta una imagen aquí, o haz clic para seleccionar
            </p>
          )}
        </div>

        {/* Fallback input file */}
        <div className="text-center">
          <span className="text-xs text-muted-foreground">O </span>
          <label
            htmlFor="file-input"
            className="text-xs text-primary cursor-pointer hover:underline"
          >
            selecciona desde tu dispositivo
          </label>
          <Input
            id="file-input"
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            className="hidden"
          />
        </div>

        <p className="text-xs text-muted-foreground">
          Selecciona una imagen (opcional). Se reemplazará la imagen actual si
          existe.
        </p>
      </div>

      {/* Botones */}
      <div className="flex justify-end gap-2">
        <motion.div
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          transition={{ type: "spring", stiffness: 400, damping: 25 }}
        >
          <Button type="submit" disabled={isSubmitting} className="relative">
            {isSubmitting && (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  ease: "linear",
                }}
                className="absolute left-3"
              >
                <Loader2 className="h-4 w-4" />
              </motion.div>
            )}
            <span className={isSubmitting ? "ml-6" : ""}>
              {isSubmitting
                ? "Guardando..."
                : mode === "create"
                  ? "Crear Producto"
                  : "Actualizar Producto"}
            </span>
          </Button>
        </motion.div>
      </div>
    </form>
  );
}
