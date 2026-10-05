import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, test } from 'vitest'
import { ashaDetail } from '../test/data'
import { mockApi, renderAt } from '../test/helpers'
import Person from './Person'

const show = () => renderAt('/people/7', '/people/:id', <Person />)

test('shows the salary timeline, newest change first', async () => {
  mockApi({ 'GET /employees/7': () => ({ body: ashaDetail }) })
  show()

  const rows = await screen.findAllByRole('row')

  expect(within(rows[1]).getByText('Annual review')).toBeVisible()
  expect(within(rows[1]).getByText('+12.5%')).toBeVisible()
  expect(within(rows[2]).getByText('Starting salary')).toBeVisible()
})

test('a salary change is saved and the page shows the new salary', async () => {
  let person = ashaDetail
  let sent: unknown
  mockApi({
    'GET /employees/7': () => ({ body: person }),
    'POST /employees/7/salary': (_url, body) => {
      sent = body
      person = { ...ashaDetail, salary: '3100000' }
      return { status: 201, body: person }
    },
  })
  const user = userEvent.setup()
  show()

  await user.click(await screen.findByRole('button', { name: 'Change salary' }))
  await user.type(screen.getByLabelText(/New annual salary \(INR\)/), '3100000')
  await user.type(screen.getByLabelText(/Reason/), 'Promotion')
  await user.click(screen.getByRole('button', { name: 'Save' }))

  expect(await screen.findByText('₹3,100,000')).toBeVisible()
  expect(sent).toMatchObject({ salary: '3100000', reason: 'Promotion' })
  await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
})

test('a refused change keeps the dialog open with the reason', async () => {
  mockApi({
    'GET /employees/7': () => ({ body: ashaDetail }),
    'POST /employees/7/salary': () => ({
      status: 409,
      body: { detail: 'That is already their salary' },
    }),
  })
  const user = userEvent.setup()
  show()

  await user.click(await screen.findByRole('button', { name: 'Change salary' }))
  await user.type(screen.getByLabelText(/New annual salary/), '2700000')
  await user.type(screen.getByLabelText(/Reason/), 'Typo')
  await user.click(screen.getByRole('button', { name: 'Save' }))

  expect(await screen.findByText('That is already their salary')).toBeVisible()
  expect(screen.getByRole('dialog')).toBeVisible()
})

test('someone who left cannot get a new salary', async () => {
  mockApi({ 'GET /employees/7': () => ({ body: { ...ashaDetail, status: 'left' } }) })
  show()

  expect(await screen.findByRole('button', { name: 'Change salary' })).toBeDisabled()
  expect(screen.getByRole('button', { name: 'Mark as current' })).toBeEnabled()
})
