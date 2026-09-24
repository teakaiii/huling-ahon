import React, { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      try {
        const response = await api.get('/api/auth/profile/')
        setUser(response.data.user)
        setIsAuthenticated(true)
      } catch (error) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        setIsAuthenticated(false)
      }
    }
    setLoading(false)
  }

  const login = async (username, password) => {
    try {
      console.log('Attempting login with:', username)
      const response = await api.post('/api/auth/login/', {
        username,
        password
      })
      
      console.log('Login response:', response.data)
      const { access, refresh } = response.data
      
      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
      
      // Get user profile after successful login
      const profileResponse = await api.get('/api/auth/profile/')
      console.log('Profile response:', profileResponse.data)
      setUser(profileResponse.data.user)
      setIsAuthenticated(true)
      console.log('User set, isAuthenticated:', true)
      
      return { success: true }
    } catch (error) {
      console.error('Login error:', error)
        const detail = error.response?.data?.detail
        const errorMessage = Array.isArray(detail)
          ? detail.join(' ')
          : detail || error.response?.data?.message || 'Invalid username or password.'
      return { 
        success: false, 
          error: errorMessage
      }
    }
  }

  const logout = async () => {
    try {
      await api.post('/api/auth/logout/', {
        refresh_token: localStorage.getItem('refresh_token')
      })
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      setUser(null)
      setIsAuthenticated(false)
    }
  }

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    logout,
    checkAuth
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
