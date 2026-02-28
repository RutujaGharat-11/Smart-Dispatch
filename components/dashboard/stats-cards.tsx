import { FileText, Truck, CheckCircle2, Clock } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

type StatsCardsProps = {
  totalRequests: number
  resourcesAvailable: number
  scheduled: number
  pending: number
}

export function StatsCards({
  totalRequests,
  resourcesAvailable,
  scheduled,
  pending,
}: StatsCardsProps) {
  const stats = [
    {
      label: "Total Requests",
      value: totalRequests,
      icon: FileText,
      color: "bg-primary/10 text-primary",
    },
    {
      label: "Resources Available",
      value: resourcesAvailable,
      icon: Truck,
      color: "bg-green-50 text-green-600",
    },
    {
      label: "Scheduled",
      value: scheduled,
      icon: CheckCircle2,
      color: "bg-blue-50 text-blue-600",
    },
    {
      label: "Pending",
      value: pending,
      icon: Clock,
      color: "bg-yellow-50 text-yellow-600",
    },
  ]

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat) => (
        <Card key={stat.label} className="border-border bg-card shadow-sm">
          <CardContent className="flex items-center gap-4 p-5">
            <div
              className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl ${stat.color}`}
            >
              <stat.icon className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{stat.label}</p>
              <p className="text-2xl font-bold text-card-foreground">
                {stat.value}
              </p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
