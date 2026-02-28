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
  location: string
  status: string
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
                <TableHead>Priority</TableHead>
                <TableHead>Location</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-muted-foreground">
                    Loading pending requests...
                  </TableCell>
                </TableRow>
              ) : requests.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-muted-foreground">
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
                      <Badge variant={getPriorityVariant(req.priority)}>
                        {req.priority}
                      </Badge>
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
