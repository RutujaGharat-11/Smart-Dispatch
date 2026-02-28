import Image from "next/image"
import Link from "next/link"

export function Footer() {
  return (
    <footer className="border-t border-border bg-card">
      <div className="mx-auto flex max-w-7xl flex-col items-center gap-6 px-6 py-10 md:flex-row md:justify-between">
        <div className="flex items-center gap-2.5">
          <Image
            src="/images/logo.png"
            alt="SmartDispatch Logo"
            width={32}
            height={32}
            className="h-8 w-8 object-contain"
          />
          <span className="text-lg font-bold tracking-tight text-foreground">
            SmartDispatch
          </span>
        </div>

        <nav className="flex items-center gap-6">
          <Link
            href="/"
            className="text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            Home
          </Link>
          <Link
            href="/request"
            className="text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            Submit Request
          </Link>
          <Link
            href="/dashboard"
            className="text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            Dashboard
          </Link>
        </nav>

        <p className="text-sm text-muted-foreground">
          {"SmartDispatch. Optimized Public Resource Scheduling."}
        </p>
      </div>
    </footer>
  )
}
