export function getApiBaseUrl(): string {
  const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL?.trim()

  if (configuredApiUrl) {
    return configuredApiUrl.replace(/\/+$/, "")
  }

  // Default to same-origin so Vercel rewrites can proxy to Render.
  return ""
}