"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

type AuthGuardProps = {
  children: React.ReactNode
  requiredRole?: "ADMIN" | "USER"
}

export function AuthGuard({ children, requiredRole }: AuthGuardProps) {
  const router = useRouter()
  const [isChecking, setIsChecking] = useState(true)

  useEffect(() => {
    let isMounted = true
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000"

    const validateSession = async () => {
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
            setIsChecking(false)
          }
          return
        }

        const data = (await response.json()) as {
          authenticated?: boolean
          role?: string
        }

        if (!data.authenticated) {
          router.replace("/login")
          return
        }

        if (requiredRole && data.role !== requiredRole) {
          router.replace("/login")
          return
        }
      } catch {
        if (isMounted) {
          setIsChecking(false)
        }
        return
      }

      if (isMounted) {
        setIsChecking(false)
      }
    }

    validateSession()

    return () => {
      isMounted = false
    }
  }, [requiredRole, router])

  if (isChecking) {
    return (
      <section className="px-6 py-10">
        <div className="mx-auto max-w-7xl text-muted-foreground">Checking session...</div>
      </section>
    )
  }

  return <>{children}</>
}
