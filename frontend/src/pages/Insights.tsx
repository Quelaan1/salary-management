import Alert from '@mui/material/Alert'
import Box from '@mui/material/Box'
import Paper from '@mui/material/Paper'
import Stack from '@mui/material/Stack'
import Table from '@mui/material/Table'
import TableBody from '@mui/material/TableBody'
import TableCell from '@mui/material/TableCell'
import TableContainer from '@mui/material/TableContainer'
import TableHead from '@mui/material/TableHead'
import TableRow from '@mui/material/TableRow'
import ToggleButton from '@mui/material/ToggleButton'
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup'
import Typography from '@mui/material/Typography'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router'
import { api } from '../api'
import type { Insights as InsightsData } from '../api'
import { money } from '../format'

const SPLITS = { country: 'Country', department: 'Department', job_title: 'Job title' }

export default function Insights() {
  const [params, setParams] = useSearchParams()
  const by = params.get('by') ?? 'country'

  const company = useQuery({
    queryKey: ['insights'],
    queryFn: () => api<InsightsData>('/insights'),
  })
  const split = useQuery({
    queryKey: ['insights', by],
    queryFn: () => api<InsightsData>(`/insights?by=${by}`),
  })

  const error = company.error ?? split.error
  const all = company.data?.groups[0]
  const usd = (amount: string) => money(Math.round(Number(amount)), 'USD')
  const groups = split.data?.groups.toSorted((a, b) => Number(b.median) - Number(a.median)) ?? []
  const highestMedian = Math.max(...groups.map((group) => Number(group.median)), 1)

  return (
    <Stack spacing={3}>
      <div>
        <Typography variant="h5">Insights</Typography>
        <Typography color="text.secondary">
          Annual pay of current employees in USD. Local salaries are converted at fixed rates, so
          the figures are approximate.
        </Typography>
      </div>

      {error && <Alert severity="error">{error.message}</Alert>}

      {all && (
        <Stack direction="row" spacing={2} useFlexGap sx={{ flexWrap: 'wrap' }}>
          <Tile label="Headcount" value={all.headcount.toLocaleString('en')} />
          <Tile label="Total annual pay" value={usd(all.total)} />
          <Tile label="Lowest" value={usd(all.lowest)} />
          <Tile label="Median" value={usd(all.median)} />
          <Tile label="Average" value={usd(all.average)} />
          <Tile label="Highest" value={usd(all.highest)} />
        </Stack>
      )}

      <ToggleButtonGroup
        exclusive
        size="small"
        value={by}
        onChange={(_event, next) => next && setParams({ by: next }, { replace: true })}
      >
        {Object.entries(SPLITS).map(([value, label]) => (
          <ToggleButton key={value} value={value}>
            By {label.toLowerCase()}
          </ToggleButton>
        ))}
      </ToggleButtonGroup>

      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>{SPLITS[by as keyof typeof SPLITS]}</TableCell>
              <TableCell align="right">Headcount</TableCell>
              <TableCell align="right">Total</TableCell>
              <TableCell align="right">Lowest</TableCell>
              <TableCell align="right">Median</TableCell>
              <TableCell sx={{ width: '18%' }} />
              <TableCell align="right">Average</TableCell>
              <TableCell align="right">Highest</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {groups.map((group) => (
              <TableRow key={group.name}>
                <TableCell>{group.name}</TableCell>
                <TableCell align="right">{group.headcount.toLocaleString('en')}</TableCell>
                <TableCell align="right">{usd(group.total)}</TableCell>
                <TableCell align="right">{usd(group.lowest)}</TableCell>
                <TableCell align="right">{usd(group.median)}</TableCell>
                <TableCell>
                  <Box
                    aria-hidden
                    sx={{
                      height: 8,
                      borderRadius: 1,
                      bgcolor: 'primary.main',
                      width: `${(Number(group.median) / highestMedian) * 100}%`,
                    }}
                  />
                </TableCell>
                <TableCell align="right">{usd(group.average)}</TableCell>
                <TableCell align="right">{usd(group.highest)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Stack>
  )
}

function Tile({ label, value }: { label: string; value: string }) {
  return (
    <Paper variant="outlined" sx={{ p: 2, minWidth: 150 }}>
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="h6">{value}</Typography>
    </Paper>
  )
}
