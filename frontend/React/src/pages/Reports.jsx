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
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
} from '@mui/material'
import {
  PictureAsPdf as PdfIcon,
  Description as ExcelIcon,
  TableChart as CsvIcon,
  Download as DownloadIcon,
} from '@mui/icons-material'
import api from '../services/api'

const Reports = () => {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [reports, setReports] = useState([])
  const [statistics, setStatistics] = useState(null)
  const [openDialog, setOpenDialog] = useState(false)
  const [reportType, setReportType] = useState('daily')
  const [fileFormat, setFileFormat] = useState('pdf')

  useEffect(() => {
    fetchReports()
    fetchStatistics()
  }, [])

  const fetchReports = async () => {
    try {
      const response = await api.get('/api/reports/')
      setReports(response.data.results || response.data)
      setError(null)
    } catch (err) {
      setError('Failed to fetch reports')
    } finally {
      setLoading(false)
    }
  }

  const fetchStatistics = async () => {
    try {
      const response = await api.get('/api/reports/statistics/')
      setStatistics(response.data)
    } catch (err) {
      console.error('Failed to fetch statistics:', err)
    }
  }

  const handleGenerateReport = async () => {
    try {
      await api.get(`/api/reports/generate/?type=${reportType}&file_format=${fileFormat}`)
      setOpenDialog(false)
      fetchReports()
      fetchStatistics()
    } catch (err) {
      setError('Failed to generate report')
    }
  }

  const handleDownloadReport = (report) => {
    api.get(`/api/reports/export/?file_format=${report.file_format}`, { responseType: 'blob' })
      .then((response) => {
        const url = window.URL.createObjectURL(response.data)
        const link = document.createElement('a')
        link.href = url
        link.download = `ahon-floodwatch-telemetry-${new Date().toISOString().replace(/[:.]/g, '-')}.${report.file_format}`
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
      })
      .catch(() => setError('Failed to download report'))
  }

  const getReportTypeColor = (type) => {
    switch (type) {
      case 'daily':
        return 'info'
      case 'weekly':
        return 'success'
      case 'monthly':
        return 'warning'
      case 'annual':
        return 'error'
      default:
        return 'default'
    }
  }

  const getFormatIcon = (format) => {
    switch (format) {
      case 'pdf':
        return <PdfIcon />
      case 'xlsx':
        return <ExcelIcon />
      case 'csv':
        return <CsvIcon />
      default:
        return <DownloadIcon />
    }
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Reports
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Generate and download flood detection reports
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<DownloadIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Generate Report
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Total Reports
              </Typography>
              <Typography variant="h4">
                {statistics?.total_reports || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Daily Reports
              </Typography>
              <Typography variant="h4">
                {statistics?.type_counts?.daily || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Weekly Reports
              </Typography>
              <Typography variant="h4">
                {statistics?.type_counts?.weekly || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Monthly Reports
              </Typography>
              <Typography variant="h4">
                {statistics?.type_counts?.monthly || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Reports Table */}
      <Card>
        <CardContent>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Report Type</TableCell>
                  <TableCell>Generated By</TableCell>
                  <TableCell>Date Range</TableCell>
                  <TableCell>Format</TableCell>
                  <TableCell>Records</TableCell>
                  <TableCell>Created At</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {reports.map((report) => (
                  <TableRow key={report.report_id}>
                    <TableCell>
                      <Chip
                        label={report.report_type}
                        color={getReportTypeColor(report.report_type)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{report.generated_by_username}</TableCell>
                    <TableCell>
                      {new Date(report.start_date).toLocaleDateString()} - {new Date(report.end_date).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        {getFormatIcon(report.file_format)}
                        <span style={{ marginLeft: 8 }}>{report.file_format?.toUpperCase()}</span>
                      </Box>
                    </TableCell>
                    <TableCell>{report.record_count}</TableCell>
                    <TableCell>
                      {new Date(report.created_at).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={<DownloadIcon />}
                        onClick={() => handleDownloadReport(report)}
                      >
                        Download
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Generate Report Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Generate Report</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Report Type</InputLabel>
              <Select
                value={reportType}
                label="Report Type"
                onChange={(e) => setReportType(e.target.value)}
              >
                <MenuItem value="daily">Daily Report</MenuItem>
                <MenuItem value="weekly">Weekly Report</MenuItem>
                <MenuItem value="monthly">Monthly Report</MenuItem>
                <MenuItem value="annual">Annual Report</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>File Format</InputLabel>
              <Select
                value={fileFormat}
                label="File Format"
                onChange={(e) => setFileFormat(e.target.value)}
              >
                <MenuItem value="pdf">PDF</MenuItem>
                <MenuItem value="xlsx">Excel (XLSX)</MenuItem>
                <MenuItem value="csv">CSV</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleGenerateReport} variant="contained">
            Generate
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Reports
