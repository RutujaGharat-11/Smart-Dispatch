"use client"

import Link from "next/link"
import { ArrowRight, LayoutDashboard } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useEffect, useState } from "react"
import { getApiBaseUrl } from "@/lib/api"

export function HeroSection() {
  const [authenticated, setAuthenticated] = useState(false)
  const [role, setRole] = useState<string | null>(null)
  const apiBaseUrl = getApiBaseUrl()

  useEffect(() => {
    let isMounted = true

    const checkAuth = async () => {
      try {
        const response = await fetch(`${apiBaseUrl}/api/check-auth`, {
          method: "GET",
          credentials: "include",
        })

        if (!response.ok) {
          if (isMounted) {
            setAuthenticated(false)
            setRole(null)
          }
          return
        }

        const data = await response.json()
        if (isMounted) {
          setAuthenticated(Boolean(data?.authenticated))
          setRole(data?.authenticated ? (data?.role ?? null) : null)
        }
      } catch {
        if (isMounted) {
          setAuthenticated(false)
          setRole(null)
        }
      }
    }

    checkAuth()

    return () => {
      isMounted = false
    }
  }, [apiBaseUrl])

  const primaryHref = !authenticated
    ? "/login"
    : role === "ADMIN"
      ? "/manage-resources"
      : "/request"

  const secondaryHref = !authenticated
    ? "/login"
    : role === "ADMIN"
      ? "/dashboard"
      : "/user-dashboard"

  return (
    <section className="relative overflow-hidden bg-primary px-6 py-24 md:py-32">
      {/* Decorative background elements */}
      <div className="pointer-events-none absolute inset-0 opacity-10">
        <div className="absolute -left-20 -top-20 h-80 w-80 rounded-full bg-accent" />
        <div className="absolute -bottom-10 -right-10 h-60 w-60 rounded-full bg-primary-foreground" />
      </div>

      <div className="relative mx-auto max-w-4xl text-center">
        <span className="mb-4 inline-block rounded-full bg-primary-foreground/15 px-4 py-1.5 text-sm font-medium text-primary-foreground">
          Public Resource Scheduling
        </span>
        <h1 className="mb-6 text-balance text-4xl font-bold leading-tight tracking-tight text-primary-foreground md:text-5xl lg:text-6xl">
          Optimized Public Resource Scheduling Platform
        </h1>
        <p className="mx-auto mb-10 max-w-2xl text-pretty text-lg leading-relaxed text-primary-foreground/80">
          Automatically schedules public resources using optimized system
          algorithms for faster and fairer service delivery.
        </p>
        <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
          <Button
            asChild
            size="lg"
            className="bg-accent text-accent-foreground hover:bg-accent/90"
          >
            <Link href={primaryHref}>
              Submit Request
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
          <Button
            asChild
            size="lg"
            variant="outline"
            className="border-primary-foreground/30 bg-transparent text-primary-foreground hover:bg-primary-foreground/10 hover:text-primary-foreground"
          >
            <Link href={secondaryHref}>
              <LayoutDashboard className="mr-2 h-4 w-4" />
              View Dashboard
            </Link>
          </Button>
        </div>
      </div>
    </section>
  )
}
