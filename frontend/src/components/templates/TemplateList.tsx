import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import { Search, FileText } from "lucide-react";
import { Input } from "@/components/ui/input";
import { useTemplatesQuery } from "@/lib/api/queries/templates";
import TemplateCard from "./TemplateCard";

export default function TemplateList() {
  const [searchTerm, setSearchTerm] = useState("");
  const { data: templates, isLoading, error } = useTemplatesQuery();

  // Filter templates based on search term
  const filteredTemplates = useMemo(() => {
    if (!templates) return [];
    if (!searchTerm.trim()) return templates;

    return templates.filter(
      (template) =>
        template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (template.description &&
          template.description
            .toLowerCase()
            .includes(searchTerm.toLowerCase())),
    );
  }, [templates, searchTerm]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <FileText className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h2 className="text-xl font-semibold">Plantillas disponibles</h2>
            <p className="text-sm text-muted-foreground">
              Elige una plantilla para crear tu inventario
            </p>
          </div>
        </div>

        <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="h-64 rounded-lg bg-muted/40 animate-pulse"
            />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <h3 className="text-lg font-medium text-muted-foreground mb-2">
          Error al cargar plantillas
        </h3>
        <p className="text-sm text-muted-foreground">
          {error instanceof Error ? error.message : "Error desconocido"}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 bg-primary/10 rounded-lg">
          <FileText className="h-5 w-5 text-primary" />
        </div>
        <div>
          <h2 className="text-xl font-semibold">Plantillas disponibles</h2>
          <p className="text-sm text-muted-foreground">
            Elige una plantilla para crear tu inventario
          </p>
        </div>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Buscar plantillas..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Templates Grid */}
      {filteredTemplates.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium text-muted-foreground mb-2">
            {searchTerm
              ? "No se encontraron plantillas"
              : "No hay plantillas disponibles"}
          </h3>
          <p className="text-sm text-muted-foreground">
            {searchTerm
              ? "Intenta con otros términos de búsqueda"
              : "Las plantillas aparecerán aquí cuando estén disponibles"}
          </p>
        </div>
      ) : (
        <motion.div
          className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          {filteredTemplates.map((template) => (
            <TemplateCard
              key={template.id}
              template={template}
              // TODO: Add inventory count when API supports it
            />
          ))}
        </motion.div>
      )}
    </div>
  );
}
