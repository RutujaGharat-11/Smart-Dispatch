"use client"

import { useCallback, useEffect, useMemo, useState } from "react"
import { StatsCards } from "@/components/dashboard/stats-cards"
import { PendingRequestsTable } from "@/components/dashboard/pending-requests-table"
import { ResourcesTable } from "@/components/dashboard/resources-table"
import { SchedulerPanel } from "@/components/dashboard/scheduler-panel"

type RequestItem = {
  id: number
  request_id: string
  name: string
  type: string
  priority: string
  location: string
  status: string
}

type ResourceItem = {
  id: number
  resource_id: string
  name: string
  type: string
  zone: string
  status: string
}

type AssignmentItem = {
  id: number
  request_id: number
  resource_id: number
  resource_name: string
  algorithm_used: string
  assigned_at: string
}

export function DashboardDataView() {
  const [requests, setRequests] = useState<RequestItem[]>([])
  const [resources, setResources] = useState<ResourceItem[]>([])
  const [assignments, setAssignments] = useState<AssignmentItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState("")

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000"

  const fetchDashboardData = useCallback(async () => {
    try {
      setErrorMessage("")
      const [requestsRes, resourcesRes, assignmentsRes] = await Promise.all([
        fetch(`${apiBaseUrl}/api/requests`, {
          method: "GET",
          credentials: "include",
        }),
        fetch(`${apiBaseUrl}/api/resources`, {
          method: "GET",
          credentials: "include",
        }),
        fetch(`${apiBaseUrl}/api/assignments`, {
          method: "GET",
          credentials: "include",
        }),
      ])

      if (!requestsRes.ok || !resourcesRes.ok || !assignmentsRes.ok) {
        throw new Error("Unable to load dashboard data")
      }

      const requestsJson = (await requestsRes.json()) as { requests?: RequestItem[] }
      const resourcesJson = (await resourcesRes.json()) as { resources?: ResourceItem[] }
      const assignmentsJson = (await assignmentsRes.json()) as {
        assignments?: AssignmentItem[]
      }

      setRequests(requestsJson.requests ?? [])
      setResources(resourcesJson.resources ?? [])
      setAssignments(assignmentsJson.assignments ?? [])
    } catch {
      setErrorMessage("Failed to load dashboard data. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }, [apiBaseUrl])

  useEffect(() => {
    fetchDashboardData()
    const intervalId = window.setInterval(fetchDashboardData, 15000)
    return () => {
      window.clearInterval(intervalId)
    }
  }, [fetchDashboardData])

  const pendingRequests = useMemo(
    () => requests.filter((request) => request.status.toLowerCase() === "pending"),
    [requests]
  )

  const availableResourcesCount = useMemo(
    () =>
      resources.filter((resource) => resource.status.toLowerCase() === "available")
        .length,
    [resources]
  )

  return (
    <div className="flex flex-col gap-8">
      {errorMessage ? (
        <p className="text-sm text-destructive">{errorMessage}</p>
      ) : null}

      <StatsCards
        totalRequests={requests.length}
        resourcesAvailable={availableResourcesCount}
        scheduled={assignments.length}
        pending={pendingRequests.length}
      />

      <div className="grid gap-8 xl:grid-cols-2">
        <PendingRequestsTable requests={pendingRequests} isLoading={isLoading} />
        <ResourcesTable resources={resources} isLoading={isLoading} />
      </div>

      <SchedulerPanel
        assignments={assignments}
        onRefresh={fetchDashboardData}
        isLoading={isLoading}
      />
    </div>
  )
}
