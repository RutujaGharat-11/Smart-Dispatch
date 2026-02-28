import { FileText, Zap, Scale } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const features = [
  {
    icon: FileText,
    title: "Report a Public Problem Easily",
    description:
      "Citizens can quickly submit service requests online without visiting any office.",
  },
  {
    icon: Zap,
    title: "Faster Help Allocation",
    description:
      "The system assigns the most suitable available government resource after submission.",
  },
  {
    icon: Scale,
    title: "Fair Service for Everyone",
    description:
      "Urgent requests are automatically prioritized to ensure fair and timely service.",
  },
]

export function FeaturesSection() {
  return (
    <section className="px-6 py-20">
      <div className="mx-auto max-w-7xl">
        <div className="mb-14 text-center">
          <h2 className="mb-3 text-3xl font-bold tracking-tight text-foreground">
            Why SmartDispatch?
          </h2>
          <p className="mx-auto max-w-xl text-muted-foreground">
            A smarter way to manage and allocate public resources efficiently.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {features.map((feature) => (
            <Card
              key={feature.title}
              className="border-border bg-card shadow-sm transition-shadow hover:shadow-md"
            >
              <CardHeader>
                <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-lg text-card-foreground">
                  {feature.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="leading-relaxed text-muted-foreground">
                  {feature.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
