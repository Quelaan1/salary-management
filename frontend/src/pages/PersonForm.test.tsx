import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, test } from 'vitest'
import { asha, filters } from '../test/data'
import { mockApi, renderAt } from '../test/helpers'
import PersonForm from './PersonForm'

const show = () => renderAt('/people/new', '/people/new', <PersonForm />)

test('the salary label names the currency of the chosen country', async () => {
  mockApi({ 'GET /filters': () => ({ body: filters }) })
  show()
  await screen.findByRole('option', { name: 'India' })

  await userEvent.setup().selectOptions(screen.getByLabelText(/Country/), 'India')

  expect(screen.getByLabelText(/Annual salary \(INR\)/)).toBeVisible()
})

test('a new person is saved and their page opens', async () => {
  let sent: unknown
  mockApi({
    'GET /filters': () => ({ body: filters }),
    'POST /employees': (_url, body) => {
      sent = body
      return { status: 201, body: asha }
    },
  })
  const user = userEvent.setup()
  show()
  await screen.findByRole('option', { name: 'India' })

  await user.type(screen.getByLabelText(/Full name/), 'Asha Rao')
  await user.type(screen.getByLabelText(/Work email/), 'asha.rao@acme.example')
  await user.selectOptions(screen.getByLabelText(/Country/), 'India')
  await user.type(screen.getByLabelText(/Department/), 'Engineering')
  await user.type(screen.getByLabelText(/Job title/), 'Software Engineer')
  await user.type(screen.getByLabelText(/Annual salary/), '2700000')
  await user.click(screen.getByRole('button', { name: 'Add person' }))

  await waitFor(() => expect(screen.getByTestId('address').textContent).toBe('/people/7'))
  expect(sent).toMatchObject({
    full_name: 'Asha Rao',
    email: 'asha.rao@acme.example',
    country: 'India',
    department: 'Engineering',
    job_title: 'Software Engineer',
    salary: '2700000',
  })
})

test('a refused person keeps the form open with the reason', async () => {
  mockApi({
    'GET /filters': () => ({ body: filters }),
    'POST /employees': () => ({
      status: 409,
      body: { detail: 'Another employee already has that email' },
    }),
  })
  const user = userEvent.setup()
  show()
  await screen.findByRole('option', { name: 'India' })

  await user.type(screen.getByLabelText(/Full name/), 'Asha Rao')
  await user.type(screen.getByLabelText(/Work email/), 'asha.rao@acme.example')
  await user.selectOptions(screen.getByLabelText(/Country/), 'India')
  await user.type(screen.getByLabelText(/Department/), 'Engineering')
  await user.type(screen.getByLabelText(/Job title/), 'Software Engineer')
  await user.type(screen.getByLabelText(/Annual salary/), '2700000')
  await user.click(screen.getByRole('button', { name: 'Add person' }))

  expect(await screen.findByText('Another employee already has that email')).toBeVisible()
  expect(screen.getByTestId('address').textContent).toBe('/people/new')
})
