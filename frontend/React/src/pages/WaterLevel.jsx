import React, { useState, useEffect } from 'react'
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  Button,
} from '@mui/material'
import WarningIcon from '@mui/icons-material/Warning'
import api from '../services/api'

const WaterLevel = () => {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [currentLevel, setCurrentLevel] = useState(null)
  const [manualSending, setManualSending] = useState(false)
  const [manualStatus, setManualStatus] = useState(null)

  useEffect(() => {
    fetchCurrentLevel()

    const interval = setInterval(fetchCurrentLevel, 10000)
    return () => clearInterval(interval)
  }, [])

  const fetchCurrentLevel = async () => {
    try {
      const response = await api.get('/api/water-level/current/')
      setCurrentLevel(response.data)
      setError(null)
    } catch (err) {
      setError('Failed to fetch current water level')
    } finally {
      setLoading(false)
    }
  }

  const sendManualWarning = async () => {
    if (!window.confirm('Send a warning SMS to all active Tonsuya residents who enabled SMS notifications?')) {
      return
    }

    setManualSending(true)
    setManualStatus(null)
    try {
      const response = await api.post('/api/alerts/manual-warning/')
      setManualStatus({
        severity: 'success',
        message: `Warning sent to ${response.data.sent || 0} resident(s).`,
      })
    } catch (err) {
      setManualStatus({
        severity: 'error',
        message: err.response?.data?.reason || 'Failed to send the manual warning.',
      })
    } finally {
      setManualSending(false)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'Normal':
        return 'success'
      case 'Alert':
        return 'info'
      case 'Warning':
        return 'warning'
      case 'Danger':
        return 'error'
      default:
        return 'default'
    }
  }

  // Reflects the sensor only. GSM is reported separately below, and is legitimately
  // disconnected on a USB-tethered setup where the sensor itself is fine.
  const sensorIsOnline = currentLevel?.sensor_status === 'online'
  const isLive = currentLevel?.source === 'firebase_sensor'

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
        Water Level Monitoring
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Live water level reading from the connected GSM sensor
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Current Water Level Card */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Typography color="textSecondary" gutterBottom variant="h6">
                  Current Water Level
                </Typography>
                <Box display="flex" alignItems="center" gap={1}>
                  <Chip
                    label={sensorIsOnline ? 'SENSOR ONLINE' : 'SENSOR OFFLINE'}
                    color={sensorIsOnline ? 'success' : 'error'}
                    size="small"
                  />
                </Box>
              </Box>
              {currentLevel ? (
                <>
                  <Typography variant="h3" sx={{ mt: 2 }}>
                    {currentLevel.water_level_cm} cm
                  </Typography>
                  <Chip
                    label={currentLevel.status}
                    color={getStatusColor(currentLevel.status)}
                    size="large"
                    sx={{ mt: 2 }}
                  />
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="body2" color="text.secondary">
                      Timestamp: {new Date(currentLevel.timestamp).toLocaleString()}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Sensor Status: {currentLevel.sensor_status}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      GSM Status: {currentLevel.gsm_status}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Source: {isLive ? 'Live sensor via Firebase' : 'Stored database reading'}
                    </Typography>
                  </Box>
                </>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No current reading available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Manual Citizen Warning */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Manual Citizen Warning
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Send a Warning SMS to active Tonsuya residents who have SMS notifications enabled.
              </Typography>
              <Button
                variant="contained"
                color="warning"
                startIcon={<WarningIcon />}
                onClick={sendManualWarning}
                disabled={manualSending}
              >
                {manualSending ? 'Sending Warning...' : 'Send Warning to Citizens'}
              </Button>
              {manualStatus && (
                <Alert severity={manualStatus.severity} sx={{ mt: 2 }}>
                  {manualStatus.message}
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

      </Grid>
    </Box>
  )
}

export default WaterLevel
