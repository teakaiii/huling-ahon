import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  Stack,
  Grid,
  Paper,
  Tooltip,
} from '@mui/material'
import {
  WbSunny,
  Cloud,
  Thunderstorm,
  Grain,
  AcUnit,
  Air,
  WaterDrop,
  BlurOn,
  WbTwilight,
  Compress,
  Visibility,
  NightsStay,
} from '@mui/icons-material'
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { fetchWeatherForecast, isHighRainRisk } from '../services/weather'

const cardSx = { borderRadius: 3, boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }

const getWeatherIcon = (code, size = 'medium') => {
  const sx = size === 'large' ? { fontSize: 56 } : size === 'small' ? { fontSize: 22 } : { fontSize: 28 }

  if ([0, 1].includes(code)) return <WbSunny sx={{ ...sx, color: 'warning.main' }} />
  if ([2, 3].includes(code)) return <Cloud sx={{ ...sx, color: 'text.secondary' }} />
  if ([45, 48].includes(code)) return <BlurOn sx={{ ...sx, color: 'text.disabled' }} />
  if ([71, 73, 75, 77, 85, 86].includes(code)) return <AcUnit sx={{ ...sx, color: 'info.main' }} />
  if ([95, 96, 99].includes(code)) return <Thunderstorm sx={{ ...sx, color: 'error.main' }} />
  if ([51, 53, 55, 61, 63, 65, 66, 67, 80, 81, 82].includes(code)) {
    return <Grain sx={{ ...sx, color: 'primary.main' }} />
  }
  return <Cloud sx={{ ...sx, color: 'text.secondary' }} />
}

const MetricTile = ({ icon, label, value, subvalue }) => (
  <Paper variant="outlined" sx={{ p: 1.5, height: '100%', borderRadius: 2 }}>
    <Box display="flex" alignItems="center" gap={1} mb={0.5}>
      {icon}
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
    </Box>
    <Typography variant="body1" fontWeight={600}>
      {value}
    </Typography>
    {subvalue && (
      <Typography variant="caption" color="text.secondary">
        {subvalue}
      </Typography>
    )}
  </Paper>
)

const WeatherForecastWidget = () => {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [weather, setWeather] = useState(null)

  const loadWeather = async () => {
    try {
      const data = await fetchWeatherForecast()
      setWeather(data)
      setError(null)
    } catch (err) {
      console.error('Weather fetch error:', err)
      setError('Unable to load weather forecast')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadWeather()
    const interval = setInterval(loadWeather, 15 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <Card sx={cardSx}>
        <CardContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight={280}>
            <CircularProgress size={32} />
            <Typography sx={{ ml: 2 }} color="text.secondary">
              Loading detailed weather forecast...
            </Typography>
          </Box>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card sx={cardSx}>
        <CardContent>
          <Alert severity="warning">{error}</Alert>
        </CardContent>
      </Card>
    )
  }

  const rainRiskDays = weather.forecast.filter((day) =>
    isHighRainRisk(day.weatherCode, day.precipitationSum)
  ).length

  const chartData = weather.hourly.map((hour) => ({
    time: hour.hourLabel,
    temp: Math.round(hour.temperature),
    rain: Number(hour.precipitation.toFixed(1)),
    rainChance: hour.precipitationProbability,
  }))

  return (
    <Card sx={cardSx}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" flexWrap="wrap" gap={2} mb={3}>
          <Box>
            <Typography variant="h6" gutterBottom>
              Weather & Flood Outlook
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {weather.location} · {weather.coordinates.latitude.toFixed(4)}°N, {weather.coordinates.longitude.toFixed(4)}°E
              {weather.elevation != null ? ` · ${Math.round(weather.elevation)} m elevation` : ''}
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
              Source: {weather.model} · Updated {new Date(weather.updatedAt).toLocaleString('en-PH')}
            </Typography>
          </Box>
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            <Chip
              label={`Flood risk: ${weather.floodRisk.level}`}
              color={weather.floodRisk.color}
              size="small"
            />
            {rainRiskDays > 0 && (
              <Chip
                label={`${rainRiskDays} high-rain day${rainRiskDays > 1 ? 's' : ''} this week`}
                color="warning"
                size="small"
              />
            )}
          </Stack>
        </Box>

        <Alert severity={weather.floodRisk.color} sx={{ mb: 3 }}>
          {weather.floodRisk.advice}
        </Alert>

        <Grid container spacing={3}>
          <Grid item xs={12} lg={4}>
            <Paper
              sx={{
                p: 3,
                height: '100%',
                borderRadius: 2,
                background: weather.current.isDay
                  ? 'linear-gradient(135deg, #e3f2fd 0%, #fff8e1 100%)'
                  : 'linear-gradient(135deg, #1a237e 0%, #283593 100%)',
                color: weather.current.isDay ? 'text.primary' : 'common.white',
              }}
            >
              <Box display="flex" alignItems="center" gap={2}>
                {getWeatherIcon(weather.current.weatherCode, 'large')}
                <Box>
                  <Typography variant="h2" lineHeight={1}>
                    {Math.round(weather.current.temperature)}°C
                  </Typography>
                  <Typography variant="body1">
                    {weather.current.description}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.85, mt: 0.5 }}>
                    Feels like {Math.round(weather.current.feelsLike)}°C
                  </Typography>
                </Box>
              </Box>
              <Divider sx={{ my: 2, borderColor: weather.current.isDay ? 'divider' : 'rgba(255,255,255,0.2)' }} />
              <Grid container spacing={1.5}>
                <Grid item xs={6}>
                  <MetricTile
                    icon={<WaterDrop fontSize="small" color="primary" />}
                    label="Humidity"
                    value={`${weather.current.humidity}%`}
                  />
                </Grid>
                <Grid item xs={6}>
                  <MetricTile
                    icon={<Grain fontSize="small" color="primary" />}
                    label="Rain now"
                    value={`${weather.current.rain} mm`}
                    subvalue={`${weather.current.precipitation} mm total`}
                  />
                </Grid>
                <Grid item xs={6}>
                  <MetricTile
                    icon={<Air fontSize="small" />}
                    label="Wind"
                    value={`${Math.round(weather.current.windSpeed)} km/h ${weather.current.windDirectionLabel}`}
                    subvalue={`Gusts ${Math.round(weather.current.windGusts)} km/h`}
                  />
                </Grid>
                <Grid item xs={6}>
                  <MetricTile
                    icon={<Compress fontSize="small" />}
                    label="Pressure"
                    value={`${Math.round(weather.current.pressure)} hPa`}
                  />
                </Grid>
                <Grid item xs={6}>
                  <MetricTile
                    icon={<Visibility fontSize="small" />}
                    label="Cloud cover"
                    value={`${weather.current.cloudCover}%`}
                  />
                </Grid>
                <Grid item xs={6}>
                  <MetricTile
                    icon={weather.current.isDay ? <WbSunny fontSize="small" color="warning" /> : <NightsStay fontSize="small" />}
                    label="UV index"
                    value={weather.current.uvIndex.toFixed(1)}
                  />
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          <Grid item xs={12} lg={5}>
            <Typography variant="subtitle1" gutterBottom>
              24-Hour Forecast
            </Typography>
            <ResponsiveContainer width="100%" height={280}>
              <ComposedChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" tick={{ fontSize: 11 }} interval={2} />
                <YAxis yAxisId="temp" tick={{ fontSize: 11 }} unit="°" />
                <YAxis yAxisId="rain" orientation="right" tick={{ fontSize: 11 }} unit="mm" />
                <ChartTooltip />
                <Legend />
                <Bar yAxisId="rain" dataKey="rain" name="Rain (mm)" fill="#1976d2" radius={[4, 4, 0, 0]} />
                <Line
                  yAxisId="temp"
                  type="monotone"
                  dataKey="temp"
                  name="Temp (°C)"
                  stroke="#ed6c02"
                  strokeWidth={2}
                  dot={false}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </Grid>

          <Grid item xs={12} lg={3}>
            <Typography variant="subtitle1" gutterBottom>
              Expected Rainfall
            </Typography>
            <Stack spacing={1.5} sx={{ mt: 1 }}>
              <Paper variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
                <Typography variant="caption" color="text.secondary">Next 24 hours</Typography>
                <Typography variant="h5" color="primary.main">{weather.rainfall.next24h} mm</Typography>
              </Paper>
              <Paper variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
                <Typography variant="caption" color="text.secondary">Next 48 hours</Typography>
                <Typography variant="h5" color="primary.main">{weather.rainfall.next48h} mm</Typography>
              </Paper>
              <Paper variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
                <Typography variant="caption" color="text.secondary">Next 7 days</Typography>
                <Typography variant="h5" color="primary.main">{weather.rainfall.next7d} mm</Typography>
              </Paper>
            </Stack>
          </Grid>

          <Grid item xs={12}>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="subtitle1" gutterBottom>
              7-Day Forecast
            </Typography>
            <Grid container spacing={1.5}>
              {weather.forecast.map((day) => (
                <Grid item xs={6} sm={4} md={3} lg={12 / 7} key={day.date}>
                  <Tooltip title={day.description}>
                    <Paper
                      variant="outlined"
                      sx={{
                        p: 1.5,
                        borderRadius: 2,
                        textAlign: 'center',
                        height: '100%',
                        bgcolor: isHighRainRisk(day.weatherCode, day.precipitationSum)
                          ? 'warning.50'
                          : 'background.paper',
                      }}
                    >
                      <Typography variant="caption" fontWeight={600} display="block">
                        {day.dayLabel}
                      </Typography>
                      <Box display="flex" justifyContent="center" my={0.5}>
                        {getWeatherIcon(day.weatherCode, 'small')}
                      </Box>
                      <Typography variant="body2" fontWeight={600}>
                        {Math.round(day.tempMax)}° / {Math.round(day.tempMin)}°
                      </Typography>
                      <Typography variant="caption" color="primary.main" display="block">
                        {day.precipitationSum} mm
                      </Typography>
                      <Typography variant="caption" color="text.secondary" display="block">
                        {day.precipitationProbability}% rain
                      </Typography>
                      <Box display="flex" justifyContent="center" alignItems="center" gap={0.5} mt={0.5}>
                        <WbTwilight sx={{ fontSize: 12, color: 'text.secondary' }} />
                        <Typography variant="caption" color="text.secondary">
                          {new Date(day.sunrise).toLocaleTimeString('en-PH', { hour: 'numeric', minute: '2-digit' })}
                        </Typography>
                      </Box>
                    </Paper>
                  </Tooltip>
                </Grid>
              ))}
            </Grid>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  )
}

export default WeatherForecastWidget
