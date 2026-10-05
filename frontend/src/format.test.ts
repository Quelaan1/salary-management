import { expect, test } from 'vitest'
import { day, money } from './format'

test('money shows the currency and drops empty decimals', () => {
  expect(money('2400000', 'INR')).toBe('₹2,400,000')
  expect(money('85000.5', 'USD')).toBe('$85,000.50')
})

test('day reads as a calendar date', () => {
  expect(day('2022-04-01')).toBe('Apr 1, 2022')
})
