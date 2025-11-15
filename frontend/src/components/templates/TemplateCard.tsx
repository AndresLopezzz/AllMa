import { useNavigate } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { FileText, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface TemplateItem {
  id: number;
  name: string;
  description?: string;
  custom_fields: Array<{
    name: string;
    type: string;
    required: boolean;
    options?: string[];
  }>;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

interface TemplateCardProps {
  template: TemplateItem;
  inventoryCount?: number; // Número de inventarios usando esta plantilla
}

export default function TemplateCard({
  template,
  inventoryCount,
}: TemplateCardProps) {
  const navigate = useNavigate();

  const handleUseTemplate = () => {
    navigate({
      to: "/inventories",
      search: { template: template.id },
    });
  };

  const formatFieldType = (type: string) => {
    const typeMap: Record<string, string> = {
      text: "Texto",
      number: "Número",
      select: "Selección",
      textarea: "Texto largo",
      date: "Fecha",
    };
    return typeMap[type] || type;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.01 }}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
    >
      <Card className="h-full flex flex-col hover:shadow-lg transition-shadow">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <FileText className="h-5 w-5 text-primary" />
              </div>
              <div>
                <CardTitle className="text-lg">{template.name}</CardTitle>
                {inventoryCount !== undefined && (
                  <Badge variant="secondary" className="mt-1">
                    {inventoryCount} inventario{inventoryCount !== 1 ? "s" : ""}
                  </Badge>
                )}
              </div>
            </div>
          </div>
          <CardDescription className="text-sm text-muted-foreground">
            {template.description ?? "Sin descripción"}
          </CardDescription>
        </CardHeader>

        <CardContent className="flex-1">
          <div className="space-y-3">
            <h4 className="font-medium text-sm">Campos personalizados:</h4>
            {template.custom_fields && template.custom_fields.length > 0 ? (
              <div className="space-y-2">
                {template.custom_fields.slice(0, 3).map((field, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between text-sm"
                  >
                    <span className="font-medium">
                      {field.name}
                      {field.required && (
                        <span className="text-destructive ml-1">*</span>
                      )}
                    </span>
                    <Badge variant="outline" className="text-xs">
                      {formatFieldType(field.type)}
                    </Badge>
                  </div>
                ))}
                {template.custom_fields.length > 3 && (
                  <p className="text-xs text-muted-foreground">
                    +{template.custom_fields.length - 3} campo
                    {template.custom_fields.length - 3 !== 1 ? "s" : ""} más
                  </p>
                )}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground italic">
                Sin campos personalizados
              </p>
            )}
          </div>
        </CardContent>

        <div className="p-6 pt-0">
          <Button onClick={handleUseTemplate} className="w-full" size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Usar en nuevo inventario
          </Button>
        </div>
      </Card>
    </motion.div>
  );
}
