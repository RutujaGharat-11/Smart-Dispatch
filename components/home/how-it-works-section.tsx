import { Send, Cpu, Eye } from "lucide-react"

const steps = [
  {
    number: "01",
    icon: Send,
    title: "Submit Request",
    description:
      "Citizens fill out a simple form describing the issue, location, and urgency level.",
  },
  {
    number: "02",
    icon: Cpu,
    title: "System Schedules Resource",
    description:
      "The scheduling algorithm processes and assigns the optimal available resource.",
  },
  {
    number: "03",
    icon: Eye,
    title: "Track Status",
    description:
      "Monitor the progress and status of every request from submission to resolution.",
  },
]

export function HowItWorksSection() {
  return (
    <section className="bg-secondary px-6 py-20">
      <div className="mx-auto max-w-7xl">
        <div className="mb-14 text-center">
          <h2 className="mb-3 text-3xl font-bold tracking-tight text-foreground">
            How It Works
          </h2>
          <p className="mx-auto max-w-xl text-muted-foreground">
            Three simple steps from request to resolution.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-3">
          {steps.map((step, index) => (
            <div key={step.title} className="relative text-center">
              {/* Connector line for desktop */}
              {index < steps.length - 1 && (
                <div className="absolute right-0 top-10 hidden h-0.5 w-full translate-x-1/2 bg-border md:block" />
              )}

              <div className="relative mx-auto mb-5 flex h-20 w-20 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-lg">
                <step.icon className="h-8 w-8" />
                <span className="absolute -right-2 -top-2 flex h-7 w-7 items-center justify-center rounded-full bg-accent text-xs font-bold text-accent-foreground">
                  {step.number}
                </span>
              </div>

              <h3 className="mb-2 text-lg font-semibold text-foreground">
                {step.title}
              </h3>
              <p className="mx-auto max-w-xs leading-relaxed text-muted-foreground">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
