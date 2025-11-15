import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/card";

export function InventoryCardSkeleton() {
  return (
    <Card>
      <CardHeader className="space-y-2">
        <div className="h-5 w-3/4 animate-pulse rounded bg-muted" />
        <div className="h-4 w-1/2 animate-pulse rounded bg-muted" />
      </CardHeader>
      <CardContent>
        <div className="h-4 w-2/3 animate-pulse rounded bg-muted" />
      </CardContent>
      <CardFooter>
        <div className="h-8 w-16 animate-pulse rounded bg-muted" />
      </CardFooter>
    </Card>
  );
}
