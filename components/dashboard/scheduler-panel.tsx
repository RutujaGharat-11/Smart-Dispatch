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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
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
  request_status?: string
  resource_status?: string
}

type ActivityLog = {
  id: number
  message: string
  created_at: string
}

type SchedulerRunResult = {
  algorithm?: string
  selected_class?: string | null
  selected_class_request_count?: number
  assigned_count?: number
  skipped_count?: number
  message?: string
}

type SchedulerPanelProps = {
  assignments: AssignmentLog[]
  logs: ActivityLog[]
  apiBaseUrl: string
  onRefresh: () => Promise<void>
  isLoading?: boolean
}

export function SchedulerPanel({
  assignments,
  logs,
  apiBaseUrl,
  onRefresh,
  isLoading = false,
}: SchedulerPanelProps) {
  const [algorithm, setAlgorithm] = useState("priority")
  const [isRunning, setIsRunning] = useState(false)
  const [completingRequestId, setCompletingRequestId] = useState<number | null>(null)
  const [actionError, setActionError] = useState("")
  const [lastRunResult, setLastRunResult] = useState<SchedulerRunResult | null>(null)

  const activityMessages = useMemo(() => {
    if (logs.length === 0) {
      return ["[System] No assignment activity yet."]
    }

    return logs.map((logItem) => {
      const timestamp = logItem.created_at
        ? new Date(logItem.created_at).toLocaleString()
        : "Unknown time"
      return `[${timestamp}] ${logItem.message}`
    })
  }, [logs])

  const scheduledAssignments = useMemo(
    () => assignments.filter((assignment) => (assignment.request_status || "").toLowerCase() === "scheduled"),
    [assignments]
  )

  async function runScheduler() {
    setIsRunning(true)
    setActionError("")
    try {
      const response = await fetch(`${apiBaseUrl}/api/run_scheduler`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ algorithm }),
      })

      if (!response.ok) {
        let apiErrorMessage = "Failed to run scheduler"
        try {
          const errorBody = (await response.json()) as {
            error?: string
            details?: string
            message?: string
          }
          if (errorBody.error && errorBody.details) {
            apiErrorMessage = `${errorBody.error}: ${errorBody.details}`
          } else if (errorBody.error) {
            apiErrorMessage = errorBody.error
          } else if (errorBody.message) {
            apiErrorMessage = errorBody.message
          }
        } catch {
          // Ignore JSON parse issues and keep fallback message.
        }
        throw new Error(apiErrorMessage)
      }

      const runResult = (await response.json()) as SchedulerRunResult
      setLastRunResult(runResult)

      await onRefresh()
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unable to run scheduler. Please try again."
      setActionError(message)
    } finally {
      setIsRunning(false)
    }
  }

  async function markAsCompleted(requestId: number) {
    setCompletingRequestId(requestId)
    setActionError("")
    try {
      const response = await fetch(`${apiBaseUrl}/api/requests/complete`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ request_id: requestId }),
      })

      if (!response.ok) {
        throw new Error("Failed to complete request")
      }

      await onRefresh()
    } catch {
      setActionError("Unable to complete request. Please try again.")
    } finally {
      setCompletingRequestId(null)
    }
  }

  return (
    <div className="flex flex-col gap-6">
      {actionError ? <p className="text-sm text-destructive">{actionError}</p> : null}

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

      {lastRunResult ? (
        <Card className="border-border bg-card shadow-sm">
          <CardHeader>
            <CardTitle className="text-card-foreground">Last Scheduler Run</CardTitle>
            <CardDescription>
              Latest class-aware dispatch result from the scheduling engine.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-3">
              <p>
                <span className="font-semibold text-foreground">Algorithm: </span>
                <span className="capitalize text-muted-foreground">{lastRunResult.algorithm || algorithm}</span>
              </p>
              <p>
                <span className="font-semibold text-foreground">Selected Class: </span>
                <span className="text-muted-foreground">{lastRunResult.selected_class || "None"}</span>
              </p>
              <p>
                <span className="font-semibold text-foreground">Class Queue Size: </span>
                <span className="text-muted-foreground">{lastRunResult.selected_class_request_count ?? 0}</span>
              </p>
              <p>
                <span className="font-semibold text-foreground">Assigned: </span>
                <span className="text-muted-foreground">{lastRunResult.assigned_count ?? 0}</span>
              </p>
              <p>
                <span className="font-semibold text-foreground">Skipped: </span>
                <span className="text-muted-foreground">{lastRunResult.skipped_count ?? 0}</span>
              </p>
              <p>
                <span className="font-semibold text-foreground">Status: </span>
                <span className="text-muted-foreground">{lastRunResult.message || "Completed"}</span>
              </p>
            </div>
          </CardContent>
        </Card>
      ) : null}

      <Card className="border-border bg-card shadow-sm">
        <CardHeader>
          <CardTitle className="text-card-foreground">Scheduled Requests</CardTitle>
          <CardDescription>
            Mark scheduled requests as completed to free the assigned resource.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Request</TableHead>
                  <TableHead>Resource</TableHead>
                  <TableHead>Algorithm</TableHead>
                  <TableHead>Assigned At</TableHead>
                  <TableHead>Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {scheduledAssignments.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center text-muted-foreground">
                      No scheduled requests available.
                    </TableCell>
                  </TableRow>
                ) : (
                  scheduledAssignments.map((assignment) => (
                    <TableRow key={assignment.id}>
                      <TableCell className="font-mono text-sm">
                        REQ-{String(assignment.request_id).padStart(3, "0")}
                      </TableCell>
                      <TableCell>{assignment.resource_name}</TableCell>
                      <TableCell className="capitalize">{assignment.algorithm_used}</TableCell>
                      <TableCell>
                        {assignment.assigned_at
                          ? new Date(assignment.assigned_at).toLocaleString()
                          : "Unknown"}
                      </TableCell>
                      <TableCell>
                        <Button
                          type="button"
                          size="sm"
                          onClick={() => {
                            markAsCompleted(assignment.request_id)
                          }}
                          disabled={completingRequestId === assignment.request_id || isLoading}
                        >
                          {completingRequestId === assignment.request_id
                            ? "Completing..."
                            : "Mark as Completed"}
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
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
              {activityMessages.map((log, i) => (
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
