import AppBar from '@mui/material/AppBar'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Container from '@mui/material/Container'
import LinearProgress from '@mui/material/LinearProgress'
import Toolbar from '@mui/material/Toolbar'
import Typography from '@mui/material/Typography'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Navigate, NavLink, Outlet, Route, Routes } from 'react-router'
import { api, ApiError } from './api'
import Login from './pages/Login'
import People from './pages/People'
import PersonForm from './pages/PersonForm'

async function signedIn(): Promise<boolean> {
  try {
    await api('/session')
    return true
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) return false
    throw error
  }
}

export default function App() {
  const session = useQuery({ queryKey: ['session'], queryFn: signedIn })

  if (session.isPending) return <LinearProgress />
  if (!session.data) return <Login />

  return (
    <Routes>
      <Route element={<Shell />}>
        <Route path="people" element={<People />} />
        <Route path="people/new" element={<PersonForm />} />
        <Route path="*" element={<Navigate to="/people" replace />} />
      </Route>
    </Routes>
  )
}

function Shell() {
  const queryClient = useQueryClient()
  const signOut = useMutation({
    mutationFn: () => api('/logout', { method: 'POST' }),
    onSuccess: () => {
      queryClient.setQueryData(['session'], false)
      // Drop cached salary data so the next person on this browser cannot see it.
      queryClient.removeQueries({ predicate: (query) => query.queryKey[0] !== 'session' })
    },
  })
  const link = { color: 'inherit', '&.active': { textDecoration: 'underline' } }

  return (
    <>
      <AppBar position="static">
        <Toolbar sx={{ gap: 1 }}>
          <Typography variant="h6" sx={{ mr: 3 }}>
            ACME salaries
          </Typography>
          <Button component={NavLink} to="/people" sx={link}>
            People
          </Button>
          <Button component={NavLink} to="/insights" sx={link}>
            Insights
          </Button>
          <Box sx={{ flexGrow: 1 }} />
          <Button color="inherit" onClick={() => signOut.mutate()}>
            Sign out
          </Button>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Outlet />
      </Container>
    </>
  )
}
