import { expect, test } from 'vitest'
import { api } from './api'
import { mockApi } from './test/helpers'

test('sends the body as JSON and returns the reply', async () => {
  let sent: unknown
  mockApi({
    'POST /employees': (_url, body) => {
      sent = body
      return { status: 201, body: { id: 1 } }
    },
  })

  const reply = await api('/employees', { method: 'POST', body: { full_name: 'Asha Rao' } })

  expect(sent).toEqual({ full_name: 'Asha Rao' })
  expect(reply).toEqual({ id: 1 })
})

test('an empty reply is not parsed', async () => {
  mockApi({ 'POST /logout': () => ({ status: 204 }) })

  expect(await api('/logout', { method: 'POST' })).toBeUndefined()
})

test('an error raised by the app keeps its message and status', async () => {
  mockApi({ 'GET /employees/9': () => ({ status: 404, body: { detail: 'No such employee' } }) })

  await expect(api('/employees/9')).rejects.toMatchObject({
    status: 404,
    message: 'No such employee',
  })
})

test('a validation error names the field', async () => {
  const detail = [{ loc: ['body', 'salary'], msg: 'Input should be greater than 0' }]
  mockApi({ 'POST /employees': () => ({ status: 422, body: { detail } }) })

  await expect(api('/employees', { method: 'POST', body: {} })).rejects.toThrow(
    'salary: Input should be greater than 0',
  )
})
