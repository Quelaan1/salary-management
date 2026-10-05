import Alert from '@mui/material/Alert'
import Button from '@mui/material/Button'
import Container from '@mui/material/Container'
import Stack from '@mui/material/Stack'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { FormEvent } from 'react'
import { api } from '../api'

export default function Login() {
  const queryClient = useQueryClient()
  const signIn = useMutation({
    mutationFn: (password: string) => api('/login', { method: 'POST', body: { password } }),
    onSuccess: () => queryClient.setQueryData(['session'], true),
  })

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    signIn.mutate(new FormData(event.currentTarget).get('password') as string)
  }

  return (
    <Container maxWidth="xs" sx={{ mt: 12 }}>
      <Stack component="form" spacing={2} onSubmit={submit}>
        <Typography variant="h5">ACME salaries</Typography>
        {signIn.isError && <Alert severity="error">{signIn.error.message}</Alert>}
        <TextField
          name="password"
          type="password"
          label="HR password"
          autoComplete="current-password"
          autoFocus
          required
        />
        <Button type="submit" variant="contained" loading={signIn.isPending}>
          Sign in
        </Button>
      </Stack>
    </Container>
  )
}
