import React, { useState, useEffect } from 'react'
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material'
import api from '../services/api'

const SMSLogs = () => {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [smsLogs, setSMSLogs] = useState([])
  const [statistics, setStatistics] = useState(null)
  const [timeRange, setTimeRange] = useState(24)
  const [filterStatus, setFilterStatus] = useState('')

  useEffect(() => {
    fetchSMSLogs()
    fetchStatistics()
  }, [timeRange])

  const fetchSMSLogs = async () => {
    try {
      const response = await api.get('/api/sms/')
      setSMSLogs(response.data.results || response.data)
      setError(null)
    } catch (err) {
      setError('Failed to fetch SMS logs')
    } finally {
      setLoading(false)
    }
  }

  const fetchStatistics = async () => {
    try {
      const response = await api.get(`/api/sms/statistics/?hours=${timeRange}`)
      setStatistics(response.data)
    } catch (err) {
      console.error('Failed to fetch statistics:', err)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'delivered':
        return 'success'
      case 'sent':
        return 'info'
      case 'pending':
        return 'warning'
      case 'failed':
        return 'error'
      default:
        return 'default'
    }
  }

  const filteredLogs = smsLogs.filter(log => {
    return !filterStatus || log.delivery_status === filterStatus
  })

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        SMS Logs
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Track SMS alert delivery and status
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Total Sent (24h)
              </Typography>
              <Typography variant="h4">
                {statistics?.total_sent || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Delivered
              </Typography>
              <Typography variant="h4">
                {statistics?.status_counts?.delivered || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Pending
              </Typography>
              <Typography variant="h4">
                {statistics?.status_counts?.pending || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Failed
              </Typography>
              <Typography variant="h4" color="error">
                {statistics?.status_counts?.failed || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Time Range</InputLabel>
                <Select
                  value={timeRange}
                  label="Time Range"
                  onChange={(e) => setTimeRange(e.target.value)}
                >
                  <MenuItem value={1}>1 Hour</MenuItem>
                  <MenuItem value={6}>6 Hours</MenuItem>
                  <MenuItem value={24}>24 Hours</MenuItem>
                  <MenuItem value={168}>1 Week</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Filter by Status</InputLabel>
                <Select
                  value={filterStatus}
                  label="Filter by Status"
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <MenuItem value="">All Status</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="sent">Sent</MenuItem>
                  <MenuItem value="delivered">Delivered</MenuItem>
                  <MenuItem value="failed">Failed</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* SMS Logs Table */}
      <Card>
        <CardContent>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Sent At</TableCell>
                  <TableCell>Recipient</TableCell>
                  <TableCell>Resident Name</TableCell>
                  <TableCell>Purok</TableCell>
                  <TableCell>Alert Level</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Message Preview</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredLogs.slice(0, 50).map((log) => (
                  <TableRow key={log.sms_id}>
                    <TableCell>
                      {new Date(log.sent_at).toLocaleString()}
                    </TableCell>
                    <TableCell>{log.recipient}</TableCell>
                    <TableCell>{log.resident_name}</TableCell>
                    <TableCell>{log.resident_purok}</TableCell>
                    <TableCell>
                      {log.alert_level && (
                        <Chip
                          label={log.alert_level}
                          size="small"
                          color={log.alert_level === 'Danger' ? 'error' : 'default'}
                        />
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={log.delivery_status}
                        color={getStatusColor(log.delivery_status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {log.message.substring(0, 50)}...
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  )
}

export default SMSLogs
