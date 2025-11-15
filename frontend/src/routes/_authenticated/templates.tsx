import { createFileRoute } from "@tanstack/react-router";
import TemplateList from "@/components/templates/TemplateList";

export const Route = createFileRoute("/_authenticated/templates")({
  component: TemplatesPage,
});

function TemplatesPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Plantillas</h1>
          <p className="text-muted-foreground mt-1">
            Explora plantillas predefinidas para crear tus inventarios
          </p>
        </div>
      </div>
      <TemplateList />
    </div>
  );
}
