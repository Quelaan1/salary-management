import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, test } from 'vitest'
import App from './App'
import { filters } from './test/data'
import { mockApi, renderAt } from './test/helpers'

test('asks for the HR password before showing any data', async () => {
  let signedIn = false
  mockApi({
    'GET /session': () => ({ status: signedIn ? 204 : 401, body: { detail: 'Sign in first' } }),
    'POST /login': (_url, body) => {
      signedIn = (body as { password: string }).password === 'right'
      return signedIn ? { status: 204 } : { status: 401, body: { detail: 'Wrong password' } }
    },
    'GET /filters': () => ({ body: filters }),
    'GET /employees': () => ({ body: { items: [], total: 0 } }),
  })
  const user = userEvent.setup()
  renderAt('/people', '*', <App />)

  await user.type(await screen.findByLabelText(/HR password/), 'wrong')
  await user.click(screen.getByRole('button', { name: 'Sign in' }))
  expect(await screen.findByText('Wrong password')).toBeVisible()

  await user.clear(screen.getByLabelText(/HR password/))
  await user.type(screen.getByLabelText(/HR password/), 'right')
  await user.click(screen.getByRole('button', { name: 'Sign in' }))
  expect(await screen.findByRole('heading', { name: 'People' })).toBeVisible()
})
