import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import type { ReactElement } from 'react'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router'
import { vi } from 'vitest'

type Reply = { status?: number; body?: unknown }
type Handler = (url: URL, body: unknown) => Reply

/** Replace fetch with canned replies, keyed by "METHOD /path". Returns the calls made. */
export function mockApi(handlers: Record<string, Handler>): string[] {
  const calls: string[] = []
  vi.stubGlobal('fetch', async (input: string, init: RequestInit = {}) => {
    const url = new URL(input, 'http://localhost')
    const key = `${init.method ?? 'GET'} ${url.pathname.replace('/api', '')}`
    calls.push(key + url.search)
    const handler = handlers[key]
    if (!handler) throw new Error(`No canned reply for ${key}`)
    const { status = 200, body } = handler(url, init.body && JSON.parse(init.body as string))
    return new Response(body === undefined ? null : JSON.stringify(body), { status })
  })
  return calls
}

function Address() {
  const location = useLocation()
  return <output data-testid="address">{location.pathname + location.search}</output>
}

/** Render a page at a route, with a fresh query cache and the current address on screen. */
export function renderAt(route: string, path: string, page: ReactElement) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[route]}>
        <Routes>
          <Route path={path} element={page} />
          <Route path="*" element={null} />
        </Routes>
        <Address />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}
