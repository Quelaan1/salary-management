import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, test } from 'vitest'
import { asha, filters } from '../test/data'
import { mockApi, renderAt } from '../test/helpers'
import People from './People'

function mockPeople(total = 1) {
  return mockApi({
    'GET /filters': () => ({ body: filters }),
    'GET /employees': () => ({ body: { items: total ? [asha] : [], total } }),
  })
}

const address = () => screen.getByTestId('address').textContent

test('lists people with their salary in their own currency', async () => {
  mockPeople()
  renderAt('/people', '/people', <People />)

  expect(await screen.findByRole('link', { name: 'Asha Rao' })).toHaveAttribute('href', '/people/7')
  expect(screen.getByText('₹2,700,000')).toBeVisible()
  expect(screen.getByText('E00007')).toBeVisible()
})

test('search goes into the address and the request', async () => {
  const calls = mockPeople()
  renderAt('/people?page=3', '/people', <People />)

  await userEvent.setup().type(screen.getByLabelText('Search name or email'), 'asha')

  await waitFor(() => expect(address()).toBe('/people?search=asha'))
  await waitFor(() => expect(calls).toContain('GET /employees?search=asha&page_size=25'))
})

test('a filter narrows the list and goes back to the first page', async () => {
  const calls = mockPeople()
  renderAt('/people?page=3', '/people', <People />)
  await screen.findByRole('option', { name: 'India' })

  await userEvent.setup().selectOptions(screen.getByLabelText('Country'), 'India')

  await waitFor(() => expect(address()).toBe('/people?country=India'))
  expect(calls).toContain('GET /employees?country=India&page_size=25')
})

test('the next page is requested from the server', async () => {
  const calls = mockPeople(60)
  renderAt('/people', '/people', <People />)
  await screen.findByText('Asha Rao')

  await userEvent.setup().click(screen.getByRole('button', { name: 'Go to next page' }))

  await waitFor(() => expect(calls).toContain('GET /employees?page=2&page_size=25'))
  expect(address()).toBe('/people?page=2')
})

test('says so when nobody matches', async () => {
  mockPeople(0)
  renderAt('/people?search=zz', '/people', <People />)

  expect(await screen.findByText('No one matches these filters.')).toBeVisible()
})
