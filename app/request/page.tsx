import type { Metadata } from "next"
import { AuthGuard } from "@/components/auth/auth-guard"
import { RequestForm } from "@/components/request/request-form"

export const metadata: Metadata = {
  title: "Submit Request - SmartDispatch",
  description: "Submit a public service request to be automatically scheduled.",
}

export default function RequestPage() {
  return (
    <AuthGuard>
      <section className="px-6 py-16">
        <div className="mx-auto max-w-7xl">
          <div className="mb-10 text-center">
            <h1 className="mb-3 text-3xl font-bold tracking-tight text-foreground">
              Submit a Service Request
            </h1>
            <p className="mx-auto max-w-xl text-muted-foreground">
              Report an issue or request a public service. The system will
              automatically schedule the best available resource.
            </p>
          </div>
          <RequestForm />
        </div>
      </section>
    </AuthGuard>
  )
}
