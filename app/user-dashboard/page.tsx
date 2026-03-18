"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Badge } from "@/components/ui/badge"
import { getApiBaseUrl } from "@/lib/api"
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

type RequestItem = {
    id: number
    request_id: string
    name: string
    type: string
    priority: string
    location: string
    status: string
    description: string
    created_at: string
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
    return status.toLowerCase() === "scheduled" || status.toLowerCase() === "completed"
        ? "bg-green-100 text-green-800"
        : "bg-yellow-100 text-yellow-800"
}

export default function UserDashboardPage() {
    const router = useRouter()
    const [isChecking, setIsChecking] = useState(true)
    const [requests, setRequests] = useState<RequestItem[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [errorMessage, setErrorMessage] = useState("")

    useEffect(() => {
        let isMounted = true
        const apiBaseUrl = getApiBaseUrl()

        const fetchUserDashboard = async () => {
            try {
                const response = await fetch(`${apiBaseUrl}/api/check-auth`, {
                    method: "GET",
                    credentials: "include",
                })

                if (response.status === 401) {
                    router.replace("/login")
                    return
                }

                if (!response.ok) {
                    if (isMounted) {
                        setErrorMessage("Unable to verify session. Please refresh.")
                        setIsChecking(false)
                        setIsLoading(false)
                    }
                    return
                }

                const authData = (await response.json()) as {
                    authenticated?: boolean
                    role?: string
                }

                if (!authData.authenticated || authData.role !== "USER") {
                    router.replace("/login")
                    return
                }

                // Fetch user's requests. If this returns 401 or 403, it means the user 
                // is not authorized as a USER role (e.g., they might be an ADMIN).
                const myRequestsRes = await fetch(`${apiBaseUrl}/api/my-requests`, {
                    method: "GET",
                    credentials: "include",
                })

                if (!myRequestsRes.ok) {
                    router.replace("/login")
                    return
                }

                const data = await myRequestsRes.json()
                if (isMounted) {
                    setRequests(data.requests || [])
                }
            } catch {
                if (isMounted) {
                    setErrorMessage("Unable to verify session. Please refresh.")
                    setIsChecking(false)
                    setIsLoading(false)
                }
                return
            }

            if (isMounted) {
                setIsChecking(false)
                setIsLoading(false)
            }
        }

        fetchUserDashboard()

        return () => {
            isMounted = false
        }
    }, [router])

    if (isChecking) {
        return (
            <section className="px-6 py-10">
                <div className="mx-auto max-w-7xl text-muted-foreground">Checking session...</div>
            </section>
        )
    }

    return (
        <section className="px-6 py-10">
            <div className="mx-auto max-w-7xl space-y-8">
                <div>
                    <h1 className="mb-2 text-3xl font-bold tracking-tight text-foreground">
                        User Dashboard
                    </h1>
                    <p className="text-muted-foreground">
                        Overview of your reported requests and their statuses.
                    </p>
                </div>

                {errorMessage ? (
                    <p className="text-sm text-destructive">{errorMessage}</p>
                ) : null}

                <Card className="border-border bg-card shadow-sm">
                    <CardHeader>
                        <CardTitle className="text-card-foreground">My Requests</CardTitle>
                        <CardDescription>
                            All requests you have submitted.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="overflow-x-auto">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>ID</TableHead>
                                        <TableHead>Type</TableHead>
                                        <TableHead>Priority</TableHead>
                                        <TableHead>Location</TableHead>
                                        <TableHead>Status</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {isLoading ? (
                                        <TableRow>
                                            <TableCell colSpan={5} className="text-center text-muted-foreground">
                                                Loading your requests...
                                            </TableCell>
                                        </TableRow>
                                    ) : requests.length === 0 ? (
                                        <TableRow>
                                            <TableCell colSpan={5} className="text-center text-muted-foreground">
                                                You have not submitted any requests yet.
                                            </TableCell>
                                        </TableRow>
                                    ) : (
                                        requests.map((req) => (
                                            <TableRow key={req.id}>
                                                <TableCell className="font-mono text-sm">{req.request_id}</TableCell>
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
            </div>
        </section>
    )
}
