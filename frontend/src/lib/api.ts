const API_URL = (import.meta.env.VITE_API_URL || '/api/v1').replace(/\/+$/, '')

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function normaliseDetail(detail: unknown): string {
  if (typeof detail === 'string') return detail

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === 'string') return item

        if (item && typeof item === 'object' && 'msg' in item) {
          return String(
            (item as { msg?: unknown }).msg || 'Validation error',
          )
        }

        return JSON.stringify(item)
      })
      .join(' • ')
  }

  if (detail && typeof detail === 'object') {
    if ('message' in detail) {
      return String(
        (detail as { message?: unknown }).message ||
          'Request failed',
      )
    }

    return JSON.stringify(detail)
  }

  return 'Request failed'
}

export async function api<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers)

  if (options.body && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }

  const cleanPath = path.startsWith('/') ? path : `/${path}`

  const response = await fetch(`${API_URL}${cleanPath}`, {
    ...options,
    headers,
    credentials: 'include',
  })

  if (response.status === 204) {
    return undefined as T
  }

  const raw = await response.text()
  let data: unknown = {}

  if (raw) {
    try {
      data = JSON.parse(raw)
    } catch {
      if (response.ok) {
        throw new ApiError(
          'AGP received an invalid API response. Please refresh and try again.',
          502,
        )
      }

      data = {
        detail: `Request failed with status ${response.status}`,
      }
    }
  }

  if (!response.ok) {
    const payload =
      data && typeof data === 'object'
        ? (data as { detail?: unknown })
        : {}

    throw new ApiError(
      normaliseDetail(payload.detail ?? data),
      response.status,
    )
  }

  return data as T
}

export { API_URL }