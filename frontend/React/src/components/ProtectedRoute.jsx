import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Box, CircularProgress } from '@mui/material'

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth()
  console.log('ProtectedRoute: loading:', loading, 'isAuthenticated:', isAuthenticated)

  if (loading) {
    console.log('ProtectedRoute: showing loading spinner')
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        <CircularProgress />
      </Box>
    )
  }

  if (!isAuthenticated) {
    console.log('ProtectedRoute: not authenticated, redirecting to login')
    return <Navigate to="/login" replace />
  }

  console.log('ProtectedRoute: authenticated, rendering children')
  return children
}

export default ProtectedRoute
