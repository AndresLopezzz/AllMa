import * as React from "react";
import { ErrorBoundary as ReactErrorBoundary } from "react-error-boundary";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";

function ErrorFallback({
  error,
  resetErrorBoundary,
}: {
  error: Error;
  resetErrorBoundary: () => void;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background text-foreground p-6">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-destructive">Algo salió mal</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">
            Ha ocurrido un error inesperado. Por favor, intenta recargar la
            página.
          </p>
          <details className="text-sm text-muted-foreground">
            <summary>Detalles del error</summary>
            <pre className="mt-2 whitespace-pre-wrap">{error.message}</pre>
          </details>
          <Button onClick={resetErrorBoundary} className="w-full">
            Recargar
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

function logError(error: Error, info: React.ErrorInfo | null) {
  // Log to console for now
  console.error("Error caught by boundary:", error, info);
  toast.error("Ha ocurrido un error en la aplicación");
}

export function ErrorBoundary({ children }: { children: React.ReactNode }) {
  return (
    <ReactErrorBoundary
      FallbackComponent={ErrorFallback}
      onError={logError}
      onReset={() => {
        // Reload the page
        window.location.reload();
      }}
    >
      {children}
    </ReactErrorBoundary>
  );
}
