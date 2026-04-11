import { Badge } from "@/components/ui/badge"
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

type PendingRequest = {
  id: number
  request_id: string
  name: string
  type: string
  priority: string
  class_of_service?: "CRITICAL" | "HIGH" | "NORMAL" | "LOW" | string
  waiting_time?: number
  execution_time?: number
  location: string
  status: string
}

function normalizeText(value?: string) {
  return String(value || "").trim().toLowerCase()
}

function resolveClassOfService(request: PendingRequest) {
  const provided = normalizeText(request.class_of_service).toUpperCase()
  if (provided === "CRITICAL" || provided === "HIGH" || provided === "NORMAL" || provided === "LOW") {
    return provided
  }

  const type = normalizeText(request.type)
  if (type.includes("ambulance") || type.includes("fire")) {
    return "CRITICAL"
  }
  if (type.includes("police")) {
    return "HIGH"
  }
  if (type.includes("agriculture")) {
    return "NORMAL"
  }
  if (type.includes("garbage")) {
    return "LOW"
  }

  return "UNCLASSIFIED"
}

function getPriorityVariant(priority: string) {
  switch (priority) {
    case "Critical":
      return "destructive"
    case "High":
      return "default"
    case "Medium":
      return "secondary"
    default:
      return "outline"
  }
}

function getStatusColor(status: string) {
  return status === "Scheduled"
    ? "bg-green-100 text-green-800"
    : "bg-yellow-100 text-yellow-800"
}

function getClassVariant(classOfService?: string) {
  switch ((classOfService || "").toUpperCase()) {
    case "CRITICAL":
      return "destructive"
    case "HIGH":
      return "default"
    case "NORMAL":
      return "secondary"
    case "UNCLASSIFIED":
      return "outline"
    default:
      return "outline"
  }
}

type PendingRequestsTableProps = {
  requests: PendingRequest[]
  isLoading?: boolean
}

export function PendingRequestsTable({
  requests,
  isLoading = false,
}: PendingRequestsTableProps) {
  return (
    <Card className="border-border bg-card shadow-sm">
      <CardHeader>
        <CardTitle className="text-card-foreground">Pending Requests</CardTitle>
        <CardDescription>
          All incoming citizen requests awaiting resource assignment.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Class</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead>Waiting</TableHead>
                <TableHead>Exec Time</TableHead>
                <TableHead>Location</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={9} className="text-center text-muted-foreground">
                    Loading pending requests...
                  </TableCell>
                </TableRow>
              ) : requests.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} className="text-center text-muted-foreground">
                    No pending requests found.
                  </TableCell>
                </TableRow>
              ) : (
                requests.map((req) => (
                  <TableRow key={req.id}>
                    <TableCell className="font-mono text-sm">{req.request_id}</TableCell>
                    <TableCell className="font-medium">{req.name}</TableCell>
                    <TableCell>{req.type}</TableCell>
                    <TableCell>
                      <Badge variant={getClassVariant(resolveClassOfService(req))}>
                        {resolveClassOfService(req)}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getPriorityVariant(req.priority)}>
                        {req.priority}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {typeof req.waiting_time === "number" ? `${req.waiting_time}m` : "0m"}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {typeof req.execution_time === "number" ? `${req.execution_time}` : "1"}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {req.location}
                    </TableCell>
                    <TableCell>
                      <span
                        className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${getStatusColor(req.status)}`}
                      >
                        {req.status}
                      </span>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}
