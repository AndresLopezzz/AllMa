// src/routes/index.tsx
import { createFileRoute } from "@tanstack/react-router";
import TemplateTest from "@/components/templates/TemplateList";

export const Route = createFileRoute("/")({
  component: Index,
});

function Index() {
  return (
    <div className="p-2">
      <h3>Home Page</h3>
      <TemplateTest />
    </div>
  );
}
