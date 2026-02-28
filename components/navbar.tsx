"use client"

import Link from "next/link"
import Image from "next/image"
import { usePathname, useRouter } from "next/navigation"
import { useState, useEffect } from "react"
import { Menu, X, LogOut } from "lucide-react"
import { cn } from "@/lib/utils"

const adminLinks = [
  { href: "/", label: "Home" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/manage-resources", label: "Manage Resources" },
]

const userLinks = [
  { href: "/", label: "Home" },
  { href: "/request", label: "Submit Request" },
  { href: "/user-dashboard", label: "User Dashboard" },
]

const guestLinks = [
  { href: "/", label: "Home" },
  { href: "/login", label: "Login" },
  { href: "/create-account", label: "Signup" },
]

export function Navbar() {
  const pathname = usePathname()
  const router = useRouter()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [authenticated, setAuthenticated] = useState(false)
  const [role, setRole] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000"
  const visibleLinks = !authenticated
      ? guestLinks
      : role === "USER"
        ? userLinks
        : role === "ADMIN"
          ? adminLinks
          : [{ href: "/", label: "Home" }]

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await fetch(`${apiBaseUrl}/api/check-auth`, {
          method: "GET",
          credentials: "include",
        })

        if (response.status === 401) {
          setAuthenticated(false)
          setRole(null)
          return
        }

        if (!response.ok) {
          setAuthenticated(false)
          setRole(null)
          return
        }

        const data = await response.json()
        setAuthenticated(Boolean(data?.authenticated))
        setRole(data?.authenticated ? (data?.role ?? null) : null)
      } catch {
        setAuthenticated(false)
        setRole(null)
      } finally {
        setLoading(false)
      }
    }
    checkAuth()
  }, [apiBaseUrl, pathname])

  const handleLogout = async () => {
    try {
      await fetch(`${apiBaseUrl}/api/logout`, {
        method: "POST",
        credentials: "include",
      })
      setAuthenticated(false)
      setRole(null)
      router.push("/login")
    } catch {
      // Ignored
    }
  }

  if (loading) {
    return null
  }

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-card/80 backdrop-blur-md">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
        <Link href="/" className="flex items-center gap-2.5">
          <Image
            src="/images/logo.png"
            alt="SmartDispatch Logo"
            width={40}
            height={40}
            className="h-10 w-10 object-contain"
          />
          <span className="text-xl font-bold tracking-tight text-foreground">
            SmartDispatch
          </span>
        </Link>

        {/* Desktop links */}
        <ul className="hidden items-center gap-1 md:flex">
          {visibleLinks.map((link) => (
            <li key={link.href}>
              <Link
                href={link.href}
                className={cn(
                  "rounded-lg px-4 py-2 text-sm font-medium transition-colors",
                  pathname === link.href
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                )}
              >
                {link.label}
              </Link>
            </li>
          ))}
          {authenticated && (
            <li>
              <Link
                href="/login"
                onClick={(event) => {
                  event.preventDefault()
                  handleLogout()
                }}
                className="flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-destructive transition-colors hover:bg-destructive/10"
              >
                <LogOut className="h-4 w-4" />
                Logout
              </Link>
            </li>
          )}
        </ul>

        {/* Mobile toggle */}
        <button
          className="rounded-lg p-2 text-foreground md:hidden"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle navigation menu"
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </nav>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="border-t border-border bg-card px-6 pb-4 pt-2 md:hidden">
          <ul className="flex flex-col gap-1">
            {visibleLinks.map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  className={cn(
                    "block rounded-lg px-4 py-2.5 text-sm font-medium transition-colors",
                    pathname === link.href
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                  )}
                >
                  {link.label}
                </Link>
              </li>
            ))}
            {authenticated && (
              <li>
                <Link
                  href="/login"
                  onClick={(event) => {
                    event.preventDefault()
                    setMobileOpen(false)
                    handleLogout()
                  }}
                  className="flex w-full items-center gap-2 rounded-lg px-4 py-2.5 text-left text-sm font-medium text-destructive transition-colors hover:bg-destructive/10"
                >
                  <LogOut className="h-4 w-4" />
                  Logout
                </Link>
              </li>
            )}
          </ul>
        </div>
      )}
    </header>
  )
}
