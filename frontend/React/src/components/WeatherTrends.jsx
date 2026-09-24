import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Tab,
  Tabs,
  FormControlLabel,
  Checkbox,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Select,
  MenuItem,
  Chip,
  CircularProgress,
} from '@mui/material'
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from 'recharts'
import { fetchWeatherForecast } from '../services/weather'
import axios from 'axios'

const cardSx = { borderRadius: 3, boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }

const generateSimulatedWeatherData = (months = 12) => {
  const data = []
  const today = new Date()
  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  
  for (let i = months - 1; i >= 0; i--) {
    const date = new Date(today.getFullYear(), today.getMonth() - i, 1)
    const monthIndex = date.getMonth()
    
    const baseTemp = 25 + Math.sin((monthIndex - 3) * Math.PI / 6) * 10
    const dailyHigh = baseTemp + Math.random() * 8 + 2
    const dailyLow = baseTemp - Math.random() * 8 - 2
    const historicalHigh = baseTemp + Math.random() * 10 + 3
    const historicalLow = baseTemp - Math.random() * 10 - 3
    const precipitation = Math.random() * (monthIndex >= 6 && monthIndex <= 9 ? 300 : 100)
    const humidity = 60 + Math.random() * 30
    const wind = 5 + Math.random() * 15
    
    data.push({
      month: monthNames[monthIndex],
      date: date.toISOString().split('T')[0],
      dailyHigh: Math.round(dailyHigh),
      dailyLow: Math.round(dailyLow),
      historicalHigh: Math.round(historicalHigh),
      historicalLow: Math.round(historicalLow),
      precipitation: Math.round(precipitation * 10) / 10,
      humidity: Math.round(humidity),
      wind: Math.round(wind * 10) / 10,
    })
  }
  
  return data
}

const fetchHistoricalWeatherData = async (months = 12) => {
  try {
    const LOCATION_NAME = import.meta.env.VITE_WEATHER_LOCATION || 'Malabon, Metro Manila'
    const FALLBACK_LAT = Number(import.meta.env.VITE_WEATHER_LAT || 14.6625)
    const FALLBACK_LON = Number(import.meta.env.VITE_WEATHER_LON || 120.9567)
    
    // Get coordinates
    let latitude = FALLBACK_LAT
    let longitude = FALLBACK_LON
    
    try {
      const geoResponse = await axios.get('https://geocoding-api.open-meteo.com/v1/search', {
        params: {
          name: LOCATION_NAME,
          count: 1,
          language: 'en',
          format: 'json',
        },
      })
      const place = geoResponse.data.results?.[0]
      if (place) {
        latitude = place.latitude
        longitude = place.longitude
      }
    } catch (err) {
      console.warn('Geocoding failed, using fallback coordinates')
    }

    // Calculate date range
    const endDate = new Date()
    const startDate = new Date()
    startDate.setMonth(startDate.getMonth() - months)
    
    const startDateStr = startDate.toISOString().split('T')[0]
    const endDateStr = endDate.toISOString().split('T')[0]

    // Fetch historical weather data
    const response = await axios.get('https://archive-api.open-meteo.com/v1/archive', {
      params: {
        latitude,
        longitude,
        start_date: startDateStr,
        end_date: endDateStr,
        daily: [
          'temperature_2m_max',
          'temperature_2m_min',
          'precipitation_sum',
          'relative_humidity_2m_mean',
          'wind_speed_10m_max',
        ].join(','),
        timezone: 'Asia/Manila',
      },
    })

    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    // Aggregate data by month
    const monthlyData = {}
    response.data.daily.time.forEach((date, index) => {
      const dateObj = new Date(date)
      const monthKey = `${dateObj.getFullYear()}-${dateObj.getMonth()}`
      
      if (!monthlyData[monthKey]) {
        monthlyData[monthKey] = {
          month: monthNames[dateObj.getMonth()],
          date: date,
          dailyHighs: [],
          dailyLows: [],
          precipitations: [],
          humidities: [],
          winds: [],
        }
      }
      
      monthlyData[monthKey].dailyHighs.push(response.data.daily.temperature_2m_max[index])
      monthlyData[monthKey].dailyLows.push(response.data.daily.temperature_2m_min[index])
      monthlyData[monthKey].precipitations.push(response.data.daily.precipitation_sum[index])
      monthlyData[monthKey].humidities.push(response.data.daily.relative_humidity_2m_mean[index])
      monthlyData[monthKey].winds.push(response.data.daily.wind_speed_10m_max[index])
    })

    // Convert to array and calculate averages
    const data = Object.values(monthlyData).map(month => ({
      month: month.month,
      date: month.date,
      dailyHigh: Math.round(Math.max(...month.dailyHighs)),
      dailyLow: Math.round(Math.min(...month.dailyLows)),
      historicalHigh: Math.round(Math.max(...month.dailyHighs)),
      historicalLow: Math.round(Math.min(...month.dailyLows)),
      precipitation: Math.round(month.precipitations.reduce((a, b) => a + b, 0) * 10) / 10,
      humidity: Math.round(month.humidities.reduce((a, b) => a + b, 0) / month.humidities.length),
      wind: Math.round(month.winds.reduce((a, b) => a + b, 0) / month.winds.length * 10) / 10,
    }))

    return data
  } catch (err) {
    console.error('Failed to fetch historical weather data:', err)
    return null
  }
}

const TabPanel = ({ children, value, index }) => {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ mt: 2 }}>{children}</Box>}
    </div>
  )
}

const WeatherTrends = () => {
  const [tabValue, setTabValue] = useState(0)
  const [timeRange, setTimeRange] = useState('12months')
  const [showDailyLow, setShowDailyLow] = useState(true)
  const [showDailyHigh, setShowDailyHigh] = useState(true)
  const [showHistorical, setShowHistorical] = useState(true)
  const [showForecast, setShowForecast] = useState(false)
  const [showConfidence, setShowConfidence] = useState(false)
  const [weatherData, setWeatherData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadHistoricalData = async () => {
      setLoading(true)
      const months = timeRange === '12months' ? 12 : 24
      const data = await fetchHistoricalWeatherData(months)
      
      if (data) {
        setWeatherData(data)
      } else {
        // Fallback to simulated data if API fails
        console.warn('Using simulated data due to API failure')
        setWeatherData(generateSimulatedWeatherData(months))
      }
      setLoading(false)
    }
    
    loadHistoricalData()
  }, [timeRange])

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue)
  }

  const getClimateInfo = () => {
    const sortedByTemp = [...weatherData].sort((a, b) => b.dailyHigh - a.dailyHigh)
    const sortedByPrecip = [...weatherData].sort((a, b) => b.precipitation - a.precipitation)
    const sortedByWind = [...weatherData].sort((a, b) => b.wind - a.wind)
    
    return {
      last12Months: {
        hottest: sortedByTemp[0]?.month || 'N/A',
        coldest: sortedByTemp[sortedByTemp.length - 1]?.month || 'N/A',
        wettest: sortedByPrecip[0]?.month || 'N/A',
        windiest: sortedByWind[0]?.month || 'N/A',
      },
      allYears: {
        hottest: 'May',
        coldest: 'January',
        wettest: 'August',
        windiest: 'December',
      },
    }
  }

  const getDailySummary = () => {
    const temps = weatherData.map(d => d.dailyHigh)
    const lows = weatherData.map(d => d.dailyLow)
    const precips = weatherData.map(d => d.precipitation)
    const winds = weatherData.map(d => d.wind)
    
    return {
      highTemp: {
        max: Math.max(...temps),
        avg: Math.round(temps.reduce((a, b) => a + b, 0) / temps.length),
        min: Math.min(...temps),
      },
      lowTemp: {
        max: Math.max(...lows),
        avg: Math.round(lows.reduce((a, b) => a + b, 0) / lows.length),
        min: Math.min(...lows),
      },
      precipitation: {
        max: Math.max(...precips),
        avg: Math.round(precips.reduce((a, b) => a + b, 0) / precips.length * 10) / 10,
        min: Math.min(...precips),
      },
      wind: {
        max: Math.max(...winds),
        avg: Math.round(winds.reduce((a, b) => a + b, 0) / winds.length * 10) / 10,
        min: Math.min(...winds),
      },
    }
  }

  const climateInfo = getClimateInfo()
  const dailySummary = getDailySummary()

  const renderTemperatureChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <AreaChart data={weatherData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="month" />
        <YAxis unit="°C" />
        <Tooltip />
        <Legend />
        {showDailyHigh && (
          <Area
            type="monotone"
            dataKey="dailyHigh"
            stackId="1"
            stroke="#ef4444"
            fill="#ef4444"
            fillOpacity={0.3}
            name="Daily High"
          />
        )}
        {showDailyLow && (
          <Area
            type="monotone"
            dataKey="dailyLow"
            stackId="2"
            stroke="#3b82f6"
            fill="#3b82f6"
            fillOpacity={0.3}
            name="Daily Low"
          />
        )}
        {showHistorical && (
          <>
            <Line
              type="monotone"
              dataKey="historicalHigh"
              stroke="#ef4444"
              strokeDasharray="5 5"
              strokeWidth={2}
              dot={false}
              name="Historical High"
            />
            <Line
              type="monotone"
              dataKey="historicalLow"
              stroke="#3b82f6"
              strokeDasharray="5 5"
              strokeWidth={2}
              dot={false}
              name="Historical Low"
            />
          </>
        )}
        <ReferenceLine x={weatherData.length - 1} stroke="#666" strokeDasharray="3 3" label="Today" />
      </AreaChart>
    </ResponsiveContainer>
  )

  const renderPrecipitationChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <AreaChart data={weatherData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="month" />
        <YAxis unit="mm" />
        <Tooltip />
        <Legend />
        <Area
          type="monotone"
          dataKey="precipitation"
          stroke="#1976d2"
          fill="#1976d2"
          fillOpacity={0.4}
          name="Precipitation"
        />
        <ReferenceLine x={weatherData.length - 1} stroke="#666" strokeDasharray="3 3" label="Today" />
      </AreaChart>
    </ResponsiveContainer>
  )

  const renderHumidityChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={weatherData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="month" />
        <YAxis unit="%" />
        <Tooltip />
        <Legend />
        <Line
          type="monotone"
          dataKey="humidity"
          stroke="#22c55e"
          strokeWidth={2}
          dot={{ fill: '#22c55e' }}
          name="Humidity"
        />
        <ReferenceLine x={weatherData.length - 1} stroke="#666" strokeDasharray="3 3" label="Today" />
      </LineChart>
    </ResponsiveContainer>
  )

  const renderWindChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={weatherData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="month" />
        <YAxis unit="km/h" />
        <Tooltip />
        <Legend />
        <Line
          type="monotone"
          dataKey="wind"
          stroke="#f59e0b"
          strokeWidth={2}
          dot={{ fill: '#f59e0b' }}
          name="Wind Speed"
        />
        <ReferenceLine x={weatherData.length - 1} stroke="#666" strokeDasharray="3 3" label="Today" />
      </LineChart>
    </ResponsiveContainer>
  )

  if (loading) {
    return (
      <Card sx={cardSx}>
        <CardContent>
          <Typography>Loading weather trends...</Typography>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card sx={cardSx}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2} mb={3}>
          <Typography variant="h6">Weather Trends</Typography>
          <Box display="flex" gap={2}>
            <Select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              size="small"
              sx={{ minWidth: 150 }}
            >
              <MenuItem value="12months">Last 12 months</MenuItem>
              <MenuItem value="24months">All months</MenuItem>
            </Select>
          </Box>
        </Box>

        <Tabs value={tabValue} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab label="Temperature" />
          <Tab label="Precipitation" />
          <Tab label="Humidity" />
          <Tab label="Wind" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          {renderTemperatureChart()}
          <Box display="flex" gap={2} mt={2} flexWrap="wrap">
            <FormControlLabel
              control={<Checkbox checked={showDailyLow} onChange={(e) => setShowDailyLow(e.target.checked)} />}
              label="Daily low"
            />
            <FormControlLabel
              control={<Checkbox checked={showDailyHigh} onChange={(e) => setShowDailyHigh(e.target.checked)} />}
              label="Daily high"
            />
            <FormControlLabel
              control={<Checkbox checked={showHistorical} onChange={(e) => setShowHistorical(e.target.checked)} />}
              label="Historical daily temperature"
            />
            <FormControlLabel
              control={<Checkbox checked={showForecast} onChange={(e) => setShowForecast(e.target.checked)} />}
              label="30 day forecast"
            />
            <FormControlLabel
              control={<Checkbox checked={showConfidence} onChange={(e) => setShowConfidence(e.target.checked)} />}
              label="Confidence"
            />
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          {renderPrecipitationChart()}
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          {renderHumidityChart()}
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          {renderWindChart()}
        </TabPanel>

        <Grid container spacing={3} mt={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" gutterBottom>Climate Information</Typography>
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Metric</TableCell>
                    <TableCell>Last 12 months</TableCell>
                    <TableCell>All Years</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell>Hottest month</TableCell>
                    <TableCell>{climateInfo.last12Months.hottest}</TableCell>
                    <TableCell>{climateInfo.allYears.hottest}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Coldest month</TableCell>
                    <TableCell>{climateInfo.last12Months.coldest}</TableCell>
                    <TableCell>{climateInfo.allYears.coldest}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Wettest month</TableCell>
                    <TableCell>{climateInfo.last12Months.wettest}</TableCell>
                    <TableCell>{climateInfo.allYears.wettest}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Windiest month</TableCell>
                    <TableCell>{climateInfo.last12Months.windiest}</TableCell>
                    <TableCell>{climateInfo.allYears.windiest}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" gutterBottom>
              Daily Summary ({timeRange === '12months' ? 'Last 12 months' : 'All months'})
            </Typography>
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Metric</TableCell>
                    <TableCell>Max</TableCell>
                    <TableCell>Average</TableCell>
                    <TableCell>Min</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell>High temperature (°C)</TableCell>
                    <TableCell>{dailySummary.highTemp.max}</TableCell>
                    <TableCell>{dailySummary.highTemp.avg}</TableCell>
                    <TableCell>{dailySummary.highTemp.min}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Low temperature (°C)</TableCell>
                    <TableCell>{dailySummary.lowTemp.max}</TableCell>
                    <TableCell>{dailySummary.lowTemp.avg}</TableCell>
                    <TableCell>{dailySummary.lowTemp.min}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Precipitation (mm)</TableCell>
                    <TableCell>{dailySummary.precipitation.max}</TableCell>
                    <TableCell>{dailySummary.precipitation.avg}</TableCell>
                    <TableCell>{dailySummary.precipitation.min}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Wind (km/h)</TableCell>
                    <TableCell>{dailySummary.wind.max}</TableCell>
                    <TableCell>{dailySummary.wind.avg}</TableCell>
                    <TableCell>{dailySummary.wind.min}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  )
}

export default WeatherTrends
