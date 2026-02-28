"use client"

import { useCallback, useEffect, useState } from "react"
import { useRouter } from "next/navigation"
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

type ResourceStatus = "free" | "busy" | "maintenance"

type ResourceItem = {
  id: number
  resource_id?: string
  name: string
  type: string
  status: string
}

const allowedStatuses: ResourceStatus[] = ["free", "busy", "maintenance"]

const statusLabels: Record<ResourceStatus, string> = {
  free: "Free",
  busy: "Busy",
  maintenance: "Maintenance",
}

function normalizeStatus(status: string): ResourceStatus {
  const normalized = status.trim().toLowerCase()

  if (normalized === "free" || normalized === "busy" || normalized === "maintenance") {
    return normalized
  }

  if (normalized === "available") {
    return "free"
  }

  if (normalized === "unavailable") {
    return "maintenance"
  }

  return "maintenance"
}

export function ManageResourcesView() {
  const router = useRouter()
  const [resources, setResources] = useState<ResourceItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState("")
  const [updatingResourceId, setUpdatingResourceId] = useState<number | null>(null)
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000"

  const fetchResources = useCallback(async () => {
    const response = await fetch(`${apiBaseUrl}/api/resources`, {
      method: "GET",
      credentials: "include",
    })

    if (!response.ok) {
      throw new Error("Failed to load resources")
    }

    const data = (await response.json()) as {
      resources?: ResourceItem[]
      authenticated?: boolean
      role?: string
    }

    setResources(data.resources ?? [])
  }, [apiBaseUrl])

  useEffect(() => {
    let isMounted = true

    const initializePage = async () => {
      try {
        setErrorMessage("")

        const authResponse = await fetch(`${apiBaseUrl}/api/check-auth`, {
          method: "GET",
          credentials: "include",
        })

        if (!authResponse.ok) {
          router.replace("/login")
          return
        }

        const authData = (await authResponse.json()) as {
          authenticated?: boolean
          role?: string
        }

        if (!authData.authenticated || authData.role !== "ADMIN") {
          router.replace("/login")
          return
        }

        await fetchResources()
      } catch {
        if (isMounted) {
          setErrorMessage("Failed to load resources. Please try again.")
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    initializePage()

    return () => {
      isMounted = false
    }
  }, [fetchResources, router])

  const handleStatusChange = useCallback(
    async (resource: ResourceItem, status: ResourceStatus) => {
      try {
        setErrorMessage("")
        setUpdatingResourceId(resource.id)

        const response = await fetch(`${apiBaseUrl}/api/resources/update-status`, {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            resource_id: resource.resource_id ?? resource.id,
            status,
          }),
        })

        if (!response.ok) {
          throw new Error("Failed to update resource status")
        }

        await fetchResources()
      } catch {
        setErrorMessage("Unable to update resource status. Please try again.")
      } finally {
        setUpdatingResourceId(null)
      }
    },
    [apiBaseUrl, fetchResources]
  )

  return (
    <Card className="border-border bg-card shadow-sm">
      <CardHeader>
        <CardTitle className="text-card-foreground">Resource Availability</CardTitle>
        <CardDescription>
          Track and update resource status for allocation operations.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {errorMessage ? <p className="mb-4 text-sm text-destructive">{errorMessage}</p> : null}

        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Resource Name</TableHead>
                <TableHead>Resource Type</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-muted-foreground">
                    Loading resources...
                  </TableCell>
                </TableRow>
              ) : resources.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-muted-foreground">
                    No resources found.
                  </TableCell>
                </TableRow>
              ) : (
                resources.map((resource) => {
                  const statusValue = normalizeStatus(resource.status)

                  return (
                    <TableRow key={resource.id}>
                      <TableCell className="font-medium">{resource.name}</TableCell>
                      <TableCell>{resource.type}</TableCell>
                      <TableCell>{statusLabels[statusValue]}</TableCell>
                      <TableCell>
                        <Select
                          value={statusValue}
                          onValueChange={(value) => {
                            handleStatusChange(resource, value as ResourceStatus)
                          }}
                          disabled={updatingResourceId === resource.id}
                        >
                          <SelectTrigger className="w-[180px]">
                            <SelectValue placeholder="Select status" />
                          </SelectTrigger>
                          <SelectContent>
                            {allowedStatuses.map((statusOption) => (
                              <SelectItem key={statusOption} value={statusOption}>
                                {statusLabels[statusOption]}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </TableCell>
                    </TableRow>
                  )
                })
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}
