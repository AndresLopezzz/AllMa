import { createFileRoute } from "@tanstack/react-router";
import TemplateList from "@/components/templates/TemplateList";

export const Route = createFileRoute("/_authenticated/templates")({
  component: TemplatesPage,
});

function TemplatesPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Plantillas</h1>
      <TemplateList />
    </div>
  );
}
