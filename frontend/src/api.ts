export type Employee = {
  id: number
  employee_number: string
  full_name: string
  email: string
  country: string
  department: string
  job_title: string
  hire_date: string
  status: 'active' | 'left'
  salary: string
  currency: string
}

export type SalaryChange = {
  id: number
  old_salary: string | null
  new_salary: string
  effective_date: string
  reason: string
}

export type EmployeeDetail = Employee & { salary_changes: SalaryChange[] }

export type EmployeePage = { items: Employee[]; total: number }

export type Filters = {
  countries: { name: string; currency: string }[]
  departments: string[]
  job_titles: string[]
}

export type Group = {
  name: string
  headcount: number
  total: string
  lowest: string
  median: string
  average: string
  highest: string
}

export type Insights = { currency: string; groups: Group[] }

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export async function api<T>(path: string, options: { method?: string; body?: unknown } = {}) {
  const hasBody = options.body !== undefined
  const response = await fetch(`/api${path}`, {
    method: options.method ?? 'GET',
    headers: hasBody ? { 'Content-Type': 'application/json' } : undefined,
    body: hasBody ? JSON.stringify(options.body) : undefined,
  })
  const data = response.status === 204 ? undefined : await response.json().catch(() => undefined)
  if (!response.ok) throw new ApiError(response.status, errorMessage(data))
  return data as T
}

// FastAPI sends a string for errors the app raises and a list for validation errors.
function errorMessage(data: unknown): string {
  const detail = (data as { detail?: unknown } | undefined)?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((item) => `${item.loc?.at(-1)}: ${item.msg}`).join('. ')
  }
  return 'Something went wrong. Try again.'
}
