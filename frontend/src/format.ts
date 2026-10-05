export function money(amount: string | number, currency: string): string {
  return new Intl.NumberFormat('en', {
    style: 'currency',
    currency,
    trailingZeroDisplay: 'stripIfInteger',
  }).format(Number(amount))
}

export function day(isoDate: string): string {
  return new Intl.DateTimeFormat('en', { dateStyle: 'medium', timeZone: 'UTC' }).format(
    new Date(isoDate),
  )
}

export function today(): string {
  const now = new Date()
  const local = new Date(now.getTime() - now.getTimezoneOffset() * 60_000)
  return local.toISOString().slice(0, 10)
}
