import type { Metadata } from "next"
import { AuthGuard } from "@/components/auth/auth-guard"
import { ManageResourcesView } from "@/components/dashboard/manage-resources-view"

export const metadata: Metadata = {
  title: "Manage Resources - SmartDispatch",
  description: "Manage resource availability for SmartDispatch operations.",
}

export default function ManageResourcesPage() {
  return (
    <AuthGuard requiredRole="ADMIN">
      <section className="px-6 py-10">
        <div className="mx-auto max-w-7xl">
          <div className="mb-8">
            <h1 className="mb-2 text-3xl font-bold tracking-tight text-foreground">
              Manage Resources
            </h1>
            <p className="text-muted-foreground">
              Update real-time resource availability and operational status.
            </p>
          </div>

          <ManageResourcesView />
        </div>
      </section>
    </AuthGuard>
  )
}
