import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, test } from 'vitest'
import { byCountry, company } from '../test/data'
import { mockApi, renderAt } from '../test/helpers'
import Insights from './Insights'

function mockInsights() {
  return mockApi({
    'GET /insights': (url) => ({ body: url.searchParams.has('by') ? byCountry : company }),
  })
}

test('shows company figures in whole USD and says they are approximate', async () => {
  mockInsights()
  renderAt('/insights', '/insights', <Insights />)

  expect(await screen.findByText('9,437')).toBeVisible()
  expect(screen.getByText('$616,521,497')).toBeVisible()
  expect(screen.getByText(/the figures are approximate/)).toBeVisible()
})

test('lists groups with the highest median first', async () => {
  mockInsights()
  renderAt('/insights', '/insights', <Insights />)
  await screen.findByText('India')

  const names = screen.getAllByRole('row').map((row) => row.firstChild?.textContent)

  expect(names).toEqual(['Country', 'United States', 'India'])
})

test('another split is requested and kept in the address', async () => {
  const calls = mockInsights()
  renderAt('/insights', '/insights', <Insights />)

  await userEvent.setup().click(screen.getByRole('button', { name: 'By department' }))

  await waitFor(() => expect(calls).toContain('GET /insights?by=department'))
  expect(screen.getByTestId('address').textContent).toBe('/insights?by=department')
})
