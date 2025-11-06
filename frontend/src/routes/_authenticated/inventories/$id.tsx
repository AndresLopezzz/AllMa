import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_authenticated/inventories/$id')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/_authenticated/inventories/$id"!</div>
}
