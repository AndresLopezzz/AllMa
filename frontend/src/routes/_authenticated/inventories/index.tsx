import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_authenticated/inventories/')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/_authenticated/inventories/"!</div>
}
