import Link from "next/link"
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

type Resource = {
  id: number
  resource_id: string
  name: string
  type: string
  zone: string
  status: string
}

function getStatusColor(status: string) {
  const normalized = status.trim().toLowerCase()
  if (normalized === "free") {
    return "bg-green-100 text-green-800"
  }
  if (normalized === "busy") {
    return "bg-yellow-100 text-yellow-800"
  }
  return "bg-red-100 text-red-800"
}

function formatStatus(status: string) {
  const normalized = status.trim().toLowerCase()
  if (normalized === "free") {
    return "Free"
  }
  if (normalized === "busy") {
    return "Busy"
  }
  return "Maintenance"
}

type ResourcesTableProps = {
  resources: Resource[]
  isLoading?: boolean
}

export function ResourcesTable({
  resources,
  isLoading = false,
}: ResourcesTableProps) {
  return (
    <Card className="border-border bg-card shadow-sm">
      <CardHeader>
        <CardTitle className="text-card-foreground">
          <Link href="/manage-resources">Resources</Link>
        </CardTitle>
        <CardDescription>
          Available government resources and their current assignment status.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Resource Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Zone</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-muted-foreground">
                    Loading resources...
                  </TableCell>
                </TableRow>
              ) : resources.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-muted-foreground">
                    No resources found.
                  </TableCell>
                </TableRow>
              ) : (
                resources.map((res) => (
                  <TableRow key={res.id}>
                    <TableCell className="font-mono text-sm">{res.resource_id}</TableCell>
                    <TableCell className="font-medium">{res.name}</TableCell>
                    <TableCell>{res.type}</TableCell>
                    <TableCell className="text-muted-foreground">
                      {res.zone}
                    </TableCell>
                    <TableCell>
                      <span
                        className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${getStatusColor(res.status)}`}
                      >
                        {formatStatus(res.status)}
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
