import { NextRequest, NextResponse } from "next/server"

export const runtime = "nodejs"
export const dynamic = "force-dynamic"

function getBackendBaseUrl(): string {
  const rawUrl =
    process.env.BACKEND_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://127.0.0.1:5000"

  return rawUrl.replace(/\/+$/, "").replace(/\/api$/i, "")
}

async function proxyRequest(
  request: NextRequest,
  params: { path: string[] }
): Promise<NextResponse> {
  const backendBaseUrl = getBackendBaseUrl()
  const backendPath = params.path.join("/")
  const targetUrl = new URL(`${backendBaseUrl}/api/${backendPath}`)
  targetUrl.search = request.nextUrl.search

  const requestHeaders = new Headers(request.headers)
  requestHeaders.delete("host")
  requestHeaders.delete("content-length")

  const init: RequestInit = {
    method: request.method,
    headers: requestHeaders,
    redirect: "manual",
  }

  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = await request.arrayBuffer()
  }

  try {
    const upstreamResponse = await fetch(targetUrl, init)
    const responseHeaders = new Headers(upstreamResponse.headers)

    return new NextResponse(upstreamResponse.body, {
      status: upstreamResponse.status,
      headers: responseHeaders,
    })
  } catch {
    return NextResponse.json(
      {
        error: "Backend is unreachable",
        details:
          "Unable to connect to backend service. Verify BACKEND_URL or NEXT_PUBLIC_API_URL in Vercel.",
      },
      { status: 502 }
    )
  }
}

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  return proxyRequest(request, await context.params)
}

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  return proxyRequest(request, await context.params)
}

export async function PUT(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  return proxyRequest(request, await context.params)
}

export async function PATCH(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  return proxyRequest(request, await context.params)
}

export async function DELETE(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  return proxyRequest(request, await context.params)
}

export async function OPTIONS(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  return proxyRequest(request, await context.params)
}