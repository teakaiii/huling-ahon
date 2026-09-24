import axios from 'axios'

const LOCATION_NAME = import.meta.env.VITE_WEATHER_LOCATION || 'Malabon, Metro Manila'
const FALLBACK_LAT = Number(import.meta.env.VITE_WEATHER_LAT || 14.6625)
const FALLBACK_LON = Number(import.meta.env.VITE_WEATHER_LON || 120.9567)
const TIMEZONE = import.meta.env.VITE_WEATHER_TIMEZONE || 'Asia/Manila'

const geocodingApi = axios.create({
  baseURL: 'https://geocoding-api.open-meteo.com/v1',
})

const weatherApi = axios.create({
  baseURL: 'https://api.open-meteo.com/v1',
})

const WEATHER_DESCRIPTIONS = {
  0: 'Clear sky',
  1: 'Mainly clear',
  2: 'Partly cloudy',
  3: 'Overcast',
  45: 'Foggy',
  48: 'Depositing rime fog',
  51: 'Light drizzle',
  53: 'Moderate drizzle',
  55: 'Dense drizzle',
  56: 'Light freezing drizzle',
  57: 'Dense freezing drizzle',
  61: 'Slight rain',
  63: 'Moderate rain',
  65: 'Heavy rain',
  66: 'Light freezing rain',
  67: 'Heavy freezing rain',
  71: 'Slight snow',
  73: 'Moderate snow',
  75: 'Heavy snow',
  77: 'Snow grains',
  80: 'Slight rain showers',
  81: 'Moderate rain showers',
  82: 'Violent rain showers',
  85: 'Slight snow showers',
  86: 'Heavy snow showers',
  95: 'Thunderstorm',
  96: 'Thunderstorm with slight hail',
  99: 'Thunderstorm with heavy hail',
}

export const getWeatherDescription = (code) =>
  WEATHER_DESCRIPTIONS[code] || 'Unknown'

export const isHighRainRisk = (code, precipitationMm = 0) =>
  [61, 63, 65, 80, 81, 82, 95, 96, 99].includes(code) || precipitationMm >= 5

export const getFloodRiskLevel = ({ rain24h, rain48h, rain7d, thunderstormDays, maxDailyRain }) => {
  let score = 0

  if (rain24h >= 20) score += 3
  else if (rain24h >= 10) score += 2
  else if (rain24h >= 5) score += 1

  if (rain48h >= 40) score += 2
  else if (rain48h >= 20) score += 1

  if (rain7d >= 100) score += 2
  else if (rain7d >= 60) score += 1

  score += Math.min(thunderstormDays, 3)
  if (maxDailyRain >= 50) score += 2
  else if (maxDailyRain >= 30) score += 1

  if (score >= 7) return { level: 'High', color: 'error', advice: 'High flood risk — prepare evacuation plans and monitor water levels closely.' }
  if (score >= 4) return { level: 'Moderate', color: 'warning', advice: 'Moderate flood risk — expect ponding and rising waterways during heavy showers.' }
  if (score >= 2) return { level: 'Low', color: 'info', advice: 'Low flood risk — stay alert for localized flooding in low-lying areas.' }
  return { level: 'Minimal', color: 'success', advice: 'Minimal flood risk from current weather conditions.' }
}

const resolveLocation = async () => {
  try {
    const response = await geocodingApi.get('/search', {
      params: {
        name: LOCATION_NAME,
        count: 1,
        language: 'en',
        format: 'json',
      },
    })

    const place = response.data.results?.[0]
    if (place) {
      return {
        latitude: place.latitude,
        longitude: place.longitude,
        location: `${place.name}${place.admin1 ? `, ${place.admin1}` : ''}`,
        elevation: place.elevation,
      }
    }
  } catch (err) {
    console.warn('Geocoding failed, using fallback coordinates:', err.message)
  }

  return {
    latitude: FALLBACK_LAT,
    longitude: FALLBACK_LON,
    location: 'Barangay Tonsuya, Malabon',
    elevation: null,
  }
}

const formatHourLabel = (isoTime) =>
  new Date(isoTime).toLocaleTimeString('en-PH', { hour: 'numeric', hour12: true })

const formatDayLabel = (date, index) => {
  if (index === 0) return 'Today'
  if (index === 1) return 'Tomorrow'
  return new Date(`${date}T12:00:00`).toLocaleDateString('en-PH', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  })
}

const windDirectionLabel = (degrees) => {
  const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
  const index = Math.round(degrees / 45) % 8
  return directions[index]
}

export const fetchWeatherForecast = async () => {
  const { latitude, longitude, location, elevation } = await resolveLocation()

  const response = await weatherApi.get('/forecast', {
    params: {
      latitude,
      longitude,
      current: [
        'temperature_2m',
        'relative_humidity_2m',
        'apparent_temperature',
        'precipitation',
        'rain',
        'weather_code',
        'cloud_cover',
        'surface_pressure',
        'wind_speed_10m',
        'wind_direction_10m',
        'wind_gusts_10m',
        'uv_index',
        'is_day',
      ].join(','),
      hourly: [
        'temperature_2m',
        'apparent_temperature',
        'precipitation',
        'precipitation_probability',
        'rain',
        'weather_code',
        'relative_humidity_2m',
        'cloud_cover',
        'wind_speed_10m',
      ].join(','),
      daily: [
        'weather_code',
        'temperature_2m_max',
        'temperature_2m_min',
        'apparent_temperature_max',
        'apparent_temperature_min',
        'precipitation_sum',
        'rain_sum',
        'precipitation_hours',
        'precipitation_probability_max',
        'wind_speed_10m_max',
        'wind_gusts_10m_max',
        'sunrise',
        'sunset',
        'uv_index_max',
      ].join(','),
      timezone: TIMEZONE,
      forecast_days: 7,
      wind_speed_unit: 'kmh',
      precipitation_unit: 'mm',
      models: 'best_match',
    },
  })

  const { current, hourly, daily, current_units: units } = response.data
  const now = new Date()

  const hourlyForecast = hourly.time
    .map((time, index) => ({
      time,
      hourLabel: formatHourLabel(time),
      temperature: hourly.temperature_2m[index],
      feelsLike: hourly.apparent_temperature[index],
      precipitation: hourly.precipitation[index],
      rain: hourly.rain[index],
      precipitationProbability: hourly.precipitation_probability[index],
      weatherCode: hourly.weather_code[index],
      description: getWeatherDescription(hourly.weather_code[index]),
      humidity: hourly.relative_humidity_2m[index],
      cloudCover: hourly.cloud_cover[index],
      windSpeed: hourly.wind_speed_10m[index],
    }))
    .filter((entry) => new Date(entry.time) >= now)
    .slice(0, 24)

  const dailyForecast = daily.time.map((date, index) => ({
    date,
    dayLabel: formatDayLabel(date, index),
    weatherCode: daily.weather_code[index],
    description: getWeatherDescription(daily.weather_code[index]),
    tempMax: daily.temperature_2m_max[index],
    tempMin: daily.temperature_2m_min[index],
    feelsLikeMax: daily.apparent_temperature_max[index],
    feelsLikeMin: daily.apparent_temperature_min[index],
    precipitationSum: daily.precipitation_sum[index],
    rainSum: daily.rain_sum[index],
    precipitationHours: daily.precipitation_hours[index],
    precipitationProbability: daily.precipitation_probability_max[index],
    windSpeedMax: daily.wind_speed_10m_max[index],
    windGustMax: daily.wind_gusts_10m_max[index],
    uvIndexMax: daily.uv_index_max[index],
    sunrise: daily.sunrise[index],
    sunset: daily.sunset[index],
  }))

  const rain24h = hourlyForecast.reduce((sum, hour) => sum + hour.precipitation, 0)
  const rain48h = hourly.time
    .slice(0, 48)
    .reduce((sum, _, index) => sum + hourly.precipitation[index], 0)
  const rain7d = dailyForecast.reduce((sum, day) => sum + day.precipitationSum, 0)
  const thunderstormDays = dailyForecast.filter((day) =>
    [95, 96, 99].includes(day.weatherCode)
  ).length
  const maxDailyRain = Math.max(...dailyForecast.map((day) => day.precipitationSum))

  return {
    location,
    coordinates: { latitude, longitude },
    elevation,
    updatedAt: new Date().toISOString(),
    model: 'Open-Meteo best_match',
    units,
    current: {
      temperature: current.temperature_2m,
      feelsLike: current.apparent_temperature,
      humidity: current.relative_humidity_2m,
      precipitation: current.precipitation,
      rain: current.rain,
      cloudCover: current.cloud_cover,
      pressure: current.surface_pressure,
      windSpeed: current.wind_speed_10m,
      windDirection: current.wind_direction_10m,
      windDirectionLabel: windDirectionLabel(current.wind_direction_10m),
      windGusts: current.wind_gusts_10m,
      uvIndex: current.uv_index,
      isDay: current.is_day === 1,
      weatherCode: current.weather_code,
      description: getWeatherDescription(current.weather_code),
    },
    hourly: hourlyForecast,
    forecast: dailyForecast,
    rainfall: {
      next24h: Number(rain24h.toFixed(1)),
      next48h: Number(rain48h.toFixed(1)),
      next7d: Number(rain7d.toFixed(1)),
    },
    floodRisk: getFloodRiskLevel({
      rain24h,
      rain48h,
      rain7d,
      thunderstormDays,
      maxDailyRain,
    }),
  }
}
