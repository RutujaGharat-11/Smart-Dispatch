import type { Metadata } from "next"
import { AuthGuard } from "@/components/auth/auth-guard"
import { DashboardDataView } from "@/components/dashboard/dashboard-data-view"

export const metadata: Metadata = {
  title: "Admin Dashboard - SmartDispatch",
  description:
    "Manage and schedule public resources with the SmartDispatch admin dashboard.",
}

export default function DashboardPage() {
  return (
    <AuthGuard requiredRole="ADMIN">
      <section className="px-6 py-10">
        <div className="mx-auto max-w-7xl">
          <div className="mb-8">
            <h1 className="mb-2 text-3xl font-bold tracking-tight text-foreground">
              Admin Dashboard
            </h1>
            <p className="text-muted-foreground">
              Overview of requests, resources, and scheduling operations.
            </p>
          </div>

          <DashboardDataView />
        </div>
      </section>
    </AuthGuard>
  )
}
