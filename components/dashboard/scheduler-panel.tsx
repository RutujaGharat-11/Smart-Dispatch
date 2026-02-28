"use client"

import { useMemo, useState } from "react"
import { Play } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { ScrollArea } from "@/components/ui/scroll-area"

const algorithms = [
  { value: "priority", label: "Priority Scheduling" },
  { value: "sjf", label: "Shortest Job First (SJF)" },
  { value: "greedy", label: "Greedy Algorithm" },
]

type AssignmentLog = {
  id: number
  request_id: number
  resource_id: number
  resource_name: string
  algorithm_used: string
  assigned_at: string
}

type SchedulerPanelProps = {
  assignments: AssignmentLog[]
  onRefresh: () => Promise<void>
  isLoading?: boolean
}

export function SchedulerPanel({
  assignments,
  onRefresh,
  isLoading = false,
}: SchedulerPanelProps) {
  const [algorithm, setAlgorithm] = useState("priority")
  const [isRunning, setIsRunning] = useState(false)

  const logs = useMemo(() => {
    if (assignments.length === 0) {
      return ["[System] No assignment activity yet."]
    }

    return assignments.map((assignment) => {
      const timestamp = assignment.assigned_at
        ? new Date(assignment.assigned_at).toLocaleString()
        : "Unknown time"
      return `[${timestamp}] REQ-${String(assignment.request_id).padStart(3, "0")} -> ${assignment.resource_name} (Algorithm: ${assignment.algorithm_used})`
    })
  }, [assignments])

  async function runScheduler() {
    setIsRunning(true)
    try {
      await onRefresh()
    } finally {
      setIsRunning(false)
    }
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Control Panel */}
      <Card className="border-border bg-card shadow-sm">
        <CardHeader>
          <CardTitle className="text-card-foreground">Control Panel</CardTitle>
          <CardDescription>
            Select a scheduling algorithm and run the scheduler.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
            <div className="flex flex-1 flex-col gap-2">
              <label
                htmlFor="algorithm"
                className="text-sm font-medium text-foreground"
              >
                Scheduling Algorithm
              </label>
              <Select value={algorithm} onValueChange={setAlgorithm}>
                <SelectTrigger id="algorithm">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {algorithms.map((algo) => (
                    <SelectItem key={algo.value} value={algo.value}>
                      {algo.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button
              onClick={runScheduler}
              disabled={isRunning || isLoading}
              size="lg"
              className="gap-2"
            >
              <Play className="h-4 w-4" />
              {isRunning ? "Running..." : "Run Scheduler"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Activity Logs */}
      <Card className="border-border bg-card shadow-sm">
        <CardHeader>
          <CardTitle className="text-card-foreground">Activity Log</CardTitle>
          <CardDescription>
            Real-time log output from the scheduling engine.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-64 rounded-lg border border-border bg-secondary p-4">
            <div className="flex flex-col gap-1">
              {logs.map((log, i) => (
                <p
                  key={i}
                  className={`font-mono text-xs leading-relaxed ${
                    log.includes("No assignment")
                      ? "text-accent"
                      : "text-muted-foreground"
                  }`}
                >
                  {log}
                </p>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  )
}
