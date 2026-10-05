# Requirements: salary management for ACME HR

## Goal

ACME's HR team keeps salary data for 10,000 employees across several countries in spreadsheets. Updates are tedious, and a question about pay means searching those sheets by hand. With this tool the HR manager keeps salaries current in one place and sees how the company pays people.

## User

The HR manager. They sign in with one shared HR account.

## Scope

1. Find people: search by name or email, filter by country, department, job title or status.
2. Keep records current: add a person, edit their details, mark them as left.
3. Change a salary: enter the new amount, the date it takes effect and a reason. The tool keeps each change, so a person's record shows their salary over time.
4. Answer pay questions: headcount, total annual pay, and the lowest, median, average and highest salary, for the whole company or by country, department or job title.

## Assumptions

- A salary is one number: annual base pay before tax.
- Each person is paid in the currency of their country.
- Company-wide figures are in USD, converted with a fixed rate table. The screen marks them as approximate.
- People who have left stay on record. Insights count current employees only.

## Left out

| Left out | Why |
| --- | --- |
| Payroll, tax, payslips | The problem is keeping and reading salary data. Paying people belongs to a payroll system. |
| Bonus, equity, benefits | One number per person keeps comparisons fair. |
| Spreadsheet import | A seed script creates the 10,000 employees for this exercise. A real rollout needs an import with validation. |
| Personal accounts, roles, approvals | The brief names one user. A shared login keeps the data private. |
| Live exchange rates | Fixed rates give the same totals on each run, so tests stay reliable. |
| Questions typed in plain English | An AI answer can get a pay figure wrong. Tested breakdowns are safer for a first version. |
