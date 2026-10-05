import type { Employee, EmployeeDetail, Filters, Insights } from '../api'

export const asha: Employee = {
  id: 7,
  employee_number: 'E00007',
  full_name: 'Asha Rao',
  email: 'asha.rao@acme.example',
  country: 'India',
  department: 'Engineering',
  job_title: 'Software Engineer',
  hire_date: '2022-04-01',
  status: 'active',
  salary: '2700000',
  currency: 'INR',
}

export const ashaDetail: EmployeeDetail = {
  ...asha,
  salary_changes: [
    {
      id: 1,
      old_salary: null,
      new_salary: '2400000',
      effective_date: '2022-04-01',
      reason: 'Starting salary',
    },
    {
      id: 2,
      old_salary: '2400000',
      new_salary: '2700000',
      effective_date: '2023-04-01',
      reason: 'Annual review',
    },
  ],
}

export const filters: Filters = {
  countries: [
    { name: 'Germany', currency: 'EUR' },
    { name: 'India', currency: 'INR' },
  ],
  departments: ['Engineering', 'Finance'],
  job_titles: ['Accountant', 'Software Engineer'],
}

export const company: Insights = {
  currency: 'USD',
  groups: [
    {
      name: 'Company',
      headcount: 9437,
      total: '616521497.33',
      lowest: '11526.48',
      median: '56843.2',
      average: '65330.24',
      highest: '251000',
    },
  ],
}

export const byCountry: Insights = {
  currency: 'USD',
  groups: [
    {
      name: 'India',
      headcount: 3311,
      total: '98044107.1',
      lowest: '11526.48',
      median: '27414.33',
      average: '29611.63',
      highest: '75000',
    },
    {
      name: 'United States',
      headcount: 2289,
      total: '225417000',
      lowest: '39000',
      median: '91000',
      average: '98478.37',
      highest: '251000',
    },
  ],
}
