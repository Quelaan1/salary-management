import Alert from '@mui/material/Alert'
import Button from '@mui/material/Button'
import Chip from '@mui/material/Chip'
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogTitle from '@mui/material/DialogTitle'
import LinearProgress from '@mui/material/LinearProgress'
import Paper from '@mui/material/Paper'
import Stack from '@mui/material/Stack'
import Table from '@mui/material/Table'
import TableBody from '@mui/material/TableBody'
import TableCell from '@mui/material/TableCell'
import TableContainer from '@mui/material/TableContainer'
import TableHead from '@mui/material/TableHead'
import TableRow from '@mui/material/TableRow'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import type { FormEvent, ReactNode } from 'react'
import { useParams } from 'react-router'
import { api } from '../api'
import type { EmployeeDetail } from '../api'
import { day, money, today } from '../format'

type Open = 'edit' | 'salary' | null

export default function Person() {
  const { id } = useParams()
  const queryClient = useQueryClient()
  const [open, setOpen] = useState<Open>(null)
  const person = useQuery({
    queryKey: ['employee', id],
    queryFn: () => api<EmployeeDetail>(`/employees/${id}`),
  })

  // One mutation for all three changes. Each one refreshes the lists and insights too.
  const save = useMutation({
    mutationFn: ({ path = '', method, body }: { path?: string; method: string; body: unknown }) =>
      api(`/employees/${id}${path}`, { method, body }),
    onSuccess: () => {
      setOpen(null)
      return queryClient.invalidateQueries()
    },
  })

  if (person.isError) return <Alert severity="error">{person.error.message}</Alert>
  if (!person.data) return <LinearProgress />

  const { data } = person
  const current = data.status === 'active'
  const timeline = data.salary_changes.toReversed()

  function submit(method: string, path?: string) {
    return (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault()
      save.mutate({ path, method, body: Object.fromEntries(new FormData(event.currentTarget)) })
    }
  }

  function close() {
    setOpen(null)
    save.reset()
  }

  function dialog(title: string, onSubmit: (event: FormEvent<HTMLFormElement>) => void, fields: ReactNode) {
    return (
      <Dialog open onClose={close} fullWidth maxWidth="xs">
        <form onSubmit={onSubmit}>
          <DialogTitle>{title}</DialogTitle>
          <DialogContent>
            <Stack spacing={2} sx={{ mt: 1 }}>
              {save.isError && <Alert severity="error">{save.error.message}</Alert>}
              {fields}
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={close}>Cancel</Button>
            <Button type="submit" variant="contained" loading={save.isPending}>
              Save
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    )
  }

  return (
    <Stack spacing={3}>
      <Stack direction="row" spacing={2} sx={{ alignItems: 'center' }}>
        <Typography variant="h5">{data.full_name}</Typography>
        <Chip label={current ? 'Current' : 'Left'} color={current ? 'success' : 'default'} />
      </Stack>

      {save.isError && open === null && <Alert severity="error">{save.error.message}</Alert>}

      <Paper variant="outlined" sx={{ p: 2 }}>
        <Stack direction="row" spacing={4} useFlexGap sx={{ flexWrap: 'wrap' }}>
          <Fact label="Employee number" value={data.employee_number} />
          <Fact label="Email" value={data.email} />
          <Fact label="Country" value={data.country} />
          <Fact label="Department" value={data.department} />
          <Fact label="Job title" value={data.job_title} />
          <Fact label="Hired" value={day(data.hire_date)} />
          <Fact label="Annual salary" value={money(data.salary, data.currency)} />
        </Stack>
      </Paper>

      <Stack direction="row" spacing={1}>
        <Button variant="contained" disabled={!current} onClick={() => setOpen('salary')}>
          Change salary
        </Button>
        <Button variant="outlined" onClick={() => setOpen('edit')}>
          Edit details
        </Button>
        <Button
          color={current ? 'error' : 'primary'}
          onClick={() =>
            save.mutate({ method: 'PATCH', body: { status: current ? 'left' : 'active' } })
          }
        >
          {current ? 'Mark as left' : 'Mark as current'}
        </Button>
      </Stack>

      <Typography variant="h6">Salary timeline</Typography>
      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Effective</TableCell>
              <TableCell align="right">From</TableCell>
              <TableCell align="right">To</TableCell>
              <TableCell align="right">Change</TableCell>
              <TableCell>Reason</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {timeline.map((row) => (
              <TableRow key={row.id}>
                <TableCell>{day(row.effective_date)}</TableCell>
                <TableCell align="right">
                  {row.old_salary === null ? '' : money(row.old_salary, data.currency)}
                </TableCell>
                <TableCell align="right">{money(row.new_salary, data.currency)}</TableCell>
                <TableCell align="right">{percentChange(row.old_salary, row.new_salary)}</TableCell>
                <TableCell>{row.reason}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {open === 'salary' &&
        dialog(
          'Change salary',
          submit('POST', '/salary'),
          <>
            <TextField
              name="salary"
              type="number"
              label={`New annual salary (${data.currency})`}
              required
              autoFocus
              slotProps={{ htmlInput: { min: 0.01, step: 0.01 } }}
            />
            <TextField
              name="effective_date"
              type="date"
              label="Effective date"
              required
              defaultValue={today()}
              slotProps={{ inputLabel: { shrink: true }, htmlInput: { max: today() } }}
            />
            <TextField name="reason" label="Reason" required />
          </>,
        )}

      {open === 'edit' &&
        dialog(
          'Edit details',
          submit('PATCH'),
          <>
            <TextField name="full_name" label="Full name" required defaultValue={data.full_name} />
            <TextField
              name="email"
              type="email"
              label="Work email"
              required
              defaultValue={data.email}
            />
            <TextField
              name="department"
              label="Department"
              required
              defaultValue={data.department}
            />
            <TextField name="job_title" label="Job title" required defaultValue={data.job_title} />
          </>,
        )}
    </Stack>
  )
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
      <Typography>{value}</Typography>
    </div>
  )
}

function percentChange(from: string | null, to: string): string {
  if (from === null) return ''
  const change = (Number(to) - Number(from)) / Number(from)
  return new Intl.NumberFormat('en', {
    style: 'percent',
    maximumFractionDigits: 1,
    signDisplay: 'always',
  }).format(change)
}
