import Alert from '@mui/material/Alert'
import Button from '@mui/material/Button'
import Chip from '@mui/material/Chip'
import Link from '@mui/material/Link'
import Paper from '@mui/material/Paper'
import Stack from '@mui/material/Stack'
import Table from '@mui/material/Table'
import TableBody from '@mui/material/TableBody'
import TableCell from '@mui/material/TableCell'
import TableContainer from '@mui/material/TableContainer'
import TableHead from '@mui/material/TableHead'
import TablePagination from '@mui/material/TablePagination'
import TableRow from '@mui/material/TableRow'
import TableSortLabel from '@mui/material/TableSortLabel'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { useRef } from 'react'
import { Link as RouterLink, useSearchParams } from 'react-router'
import { api } from '../api'
import type { EmployeePage, Filters } from '../api'
import { day, money } from '../format'

const PAGE_SIZE = 25

export default function People() {
  // The filters live in the URL, so a view can be bookmarked or shared.
  const [params, setParams] = useSearchParams()
  const searchTimer = useRef<number>(undefined)

  const filters = useQuery({ queryKey: ['filters'], queryFn: () => api<Filters>('/filters') })
  // The URL uses the same names as the API, so the query string passes straight through.
  const query = new URLSearchParams(params)
  query.set('page_size', String(PAGE_SIZE))
  const people = useQuery({
    queryKey: ['employees', query.toString()],
    queryFn: () => api<EmployeePage>(`/employees?${query}`),
    placeholderData: keepPreviousData,
  })

  function set(name: string, value: string) {
    setParams(
      (current) => {
        const next = new URLSearchParams(current)
        if (value) next.set(name, value)
        else next.delete(name)
        if (name !== 'page') next.delete('page')
        return next
      },
      { replace: true },
    )
  }

  function search(text: string) {
    window.clearTimeout(searchTimer.current)
    searchTimer.current = window.setTimeout(() => set('search', text.trim()), 300)
  }

  const sort = params.get('sort') ?? 'name'
  const page = Number(params.get('page') ?? 1)

  function sortHeader(label: string, column: string) {
    const active = sort === column || sort === `-${column}`
    const descending = sort === `-${column}`
    return (
      <TableSortLabel
        active={active}
        direction={descending ? 'desc' : 'asc'}
        onClick={() => set('sort', active && !descending ? `-${column}` : column)}
      >
        {label}
      </TableSortLabel>
    )
  }

  function select(label: string, name: string, options: { value: string; label: string }[]) {
    return (
      <TextField
        select
        size="small"
        label={label}
        value={params.get(name) ?? ''}
        onChange={(event) => set(name, event.target.value)}
        slotProps={{ select: { native: true }, inputLabel: { shrink: true } }}
        sx={{ minWidth: 160 }}
      >
        <option value="">All</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </TextField>
    )
  }

  const same = (values: string[] = []) => values.map((value) => ({ value, label: value }))

  return (
    <Stack spacing={2}>
      <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5">People</Typography>
        <Button variant="contained" component={RouterLink} to="/people/new">
          Add person
        </Button>
      </Stack>

      <Stack direction="row" spacing={2} useFlexGap sx={{ flexWrap: 'wrap' }}>
        <TextField
          size="small"
          label="Search name or email"
          defaultValue={params.get('search') ?? ''}
          onChange={(event) => search(event.target.value)}
          sx={{ minWidth: 240 }}
        />
        {select('Country', 'country', same(filters.data?.countries.map((c) => c.name)))}
        {select('Department', 'department', same(filters.data?.departments))}
        {select('Job title', 'job_title', same(filters.data?.job_titles))}
        {select('Status', 'status', [
          { value: 'active', label: 'Current' },
          { value: 'left', label: 'Left' },
        ])}
      </Stack>

      {people.isError && <Alert severity="error">{people.error.message}</Alert>}

      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>No.</TableCell>
              <TableCell>{sortHeader('Name', 'name')}</TableCell>
              <TableCell>Country</TableCell>
              <TableCell>Department</TableCell>
              <TableCell>Job title</TableCell>
              <TableCell>{sortHeader('Hired', 'hire_date')}</TableCell>
              <TableCell align="right">Annual salary</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {people.data?.items.map((person) => (
              <TableRow key={person.id} hover>
                <TableCell>{person.employee_number}</TableCell>
                <TableCell>
                  <Link component={RouterLink} to={`/people/${person.id}`}>
                    {person.full_name}
                  </Link>
                  {person.status === 'left' && <Chip label="Left" size="small" sx={{ ml: 1 }} />}
                </TableCell>
                <TableCell>{person.country}</TableCell>
                <TableCell>{person.department}</TableCell>
                <TableCell>{person.job_title}</TableCell>
                <TableCell>{day(person.hire_date)}</TableCell>
                <TableCell align="right">{money(person.salary, person.currency)}</TableCell>
              </TableRow>
            ))}
            {people.data?.total === 0 && (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  No one matches these filters.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={people.data?.total ?? 0}
          page={people.data ? page - 1 : 0}
          rowsPerPage={PAGE_SIZE}
          rowsPerPageOptions={[PAGE_SIZE]}
          onPageChange={(_event, next) => set('page', next === 0 ? '' : String(next + 1))}
        />
      </TableContainer>
    </Stack>
  )
}
