import { Skeleton } from "@/components/ui/skeleton";

export function ProductTableSkeleton() {
  return (
    <div className="overflow-x-auto">
      <table className="w-full table-auto">
        <thead>
          <tr className="text-left text-sm text-muted-foreground border-b">
            <th className="p-2">
              <Skeleton className="h-4 w-12" />
            </th>
            <th className="p-2">
              <Skeleton className="h-4 w-16" />
            </th>
            <th className="p-2">
              <Skeleton className="h-4 w-12" />
            </th>
            <th className="p-2">
              <Skeleton className="h-4 w-16" />
            </th>
            <th className="p-2">
              <Skeleton className="h-4 w-12" />
            </th>
            <th className="p-2">
              <Skeleton className="h-4 w-16" />
            </th>
            <th className="p-2">
              <Skeleton className="h-4 w-16" />
            </th>
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: 8 }).map((_, index) => (
            <tr key={index} className="odd:bg-muted/5">
              <td className="p-2">
                <Skeleton className="h-10 w-10 rounded" />
              </td>
              <td className="p-2">
                <Skeleton className="h-4 w-24" />
              </td>
              <td className="p-2">
                <Skeleton className="h-4 w-16" />
              </td>
              <td className="p-2">
                <Skeleton className="h-4 w-12" />
              </td>
              <td className="p-2">
                <Skeleton className="h-4 w-14" />
              </td>
              <td className="p-2">
                <Skeleton className="h-4 w-20" />
              </td>
              <td className="p-2">
                <div className="flex gap-2">
                  <Skeleton className="h-8 w-8" />
                  <Skeleton className="h-8 w-8" />
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
