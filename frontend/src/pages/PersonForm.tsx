import Alert from '@mui/material/Alert'
import Button from '@mui/material/Button'
import Stack from '@mui/material/Stack'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link as RouterLink, useNavigate } from 'react-router'
import { api } from '../api'
import type { Employee, Filters } from '../api'
import { today } from '../format'

export default function PersonForm() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [country, setCountry] = useState('')
  const filters = useQuery({ queryKey: ['filters'], queryFn: () => api<Filters>('/filters') })
  const currency = filters.data?.countries.find((item) => item.name === country)?.currency

  const add = useMutation({
    mutationFn: (body: unknown) => api<Employee>('/employees', { method: 'POST', body }),
    onSuccess: (person) => {
      queryClient.invalidateQueries()
      navigate(`/people/${person.id}`)
    },
  })

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    add.mutate(Object.fromEntries(new FormData(event.currentTarget)))
  }

  return (
    <Stack component="form" spacing={2} onSubmit={submit} sx={{ maxWidth: 480 }}>
      <Typography variant="h5">Add person</Typography>
      {add.isError && <Alert severity="error">{add.error.message}</Alert>}

      <TextField name="full_name" label="Full name" required />
      <TextField name="email" type="email" label="Work email" required />
      <TextField
        select
        name="country"
        label="Country"
        required
        value={country}
        onChange={(event) => setCountry(event.target.value)}
        slotProps={{ select: { native: true }, inputLabel: { shrink: true } }}
        helperText="The country sets the currency. It cannot change later."
      >
        <option value="" />
        {filters.data?.countries.map((item) => (
          <option key={item.name}>{item.name}</option>
        ))}
      </TextField>
      <TextField
        name="department"
        label="Department"
        required
        slotProps={{ htmlInput: { list: 'departments' } }}
      />
      <datalist id="departments">
        {filters.data?.departments.map((name) => (
          <option key={name} value={name} />
        ))}
      </datalist>
      <TextField
        name="job_title"
        label="Job title"
        required
        slotProps={{ htmlInput: { list: 'job-titles' } }}
      />
      <datalist id="job-titles">
        {filters.data?.job_titles.map((name) => (
          <option key={name} value={name} />
        ))}
      </datalist>
      <TextField
        name="hire_date"
        type="date"
        label="Hire date"
        required
        defaultValue={today()}
        slotProps={{ inputLabel: { shrink: true } }}
      />
      <TextField
        name="salary"
        type="number"
        label={currency ? `Annual salary (${currency})` : 'Annual salary'}
        required
        slotProps={{ htmlInput: { min: 0.01, step: 0.01 } }}
      />

      <Stack direction="row" spacing={1}>
        <Button type="submit" variant="contained" loading={add.isPending}>
          Add person
        </Button>
        <Button component={RouterLink} to="/people">
          Cancel
        </Button>
      </Stack>
    </Stack>
  )
}
