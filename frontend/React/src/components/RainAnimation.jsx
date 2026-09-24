import React, { useEffect, useRef } from 'react'
import { Box } from '@mui/material'
import { keyframes } from '@emotion/react'

const rainDrop = keyframes`
  0% {
    transform: translateY(-100vh) translateX(0);
    opacity: 1;
  }
  100% {
    transform: translateY(100vh) translateX(-20px);
    opacity: 0.3;
  }
`

const RainAnimation = ({ intensity = 'medium', size = 'full' }) => {
  const containerRef = useRef(null)
  const rainDropsRef = useRef([])

  const intensityConfig = {
    light: { count: 50, speed: 1.5, opacity: 0.3 },
    medium: { count: 100, speed: 1, opacity: 0.5 },
    heavy: { count: 200, speed: 0.7, opacity: 0.7 },
  }

  const config = intensityConfig[intensity] || intensityConfig.medium

  useEffect(() => {
    if (!containerRef.current) return

    // Clear existing rain drops
    rainDropsRef.current.forEach(drop => {
      if (drop && drop.parentNode) {
        drop.parentNode.removeChild(drop)
      }
    })
    rainDropsRef.current = []

    // Create rain drops
    const container = containerRef.current
    const { count, speed, opacity } = config

    for (let i = 0; i < count; i++) {
      const drop = document.createElement('div')
      drop.style.position = 'absolute'
      drop.style.width = '2px'
      drop.style.height = `${Math.random() * 15 + 10}px`
      drop.style.background = 'linear-gradient(to bottom, transparent, rgba(174, 194, 224, 0.8))'
      drop.style.left = `${Math.random() * 100}%`
      drop.style.top = '-20px'
      drop.style.borderRadius = '2px'
      drop.style.opacity = opacity
      drop.style.animation = `${rainDrop} ${Math.random() * 1 + speed}s linear infinite`
      drop.style.animationDelay = `${Math.random() * 2}s`
      
      container.appendChild(drop)
      rainDropsRef.current.push(drop)
    }

    return () => {
      rainDropsRef.current.forEach(drop => {
        if (drop && drop.parentNode) {
          drop.parentNode.removeChild(drop)
        }
      })
    }
  }, [intensity])

  const sizeStyles = {
    full: { height: '100%', width: '100%' },
    medium: { height: '200px', width: '100%' },
    small: { height: '100px', width: '100%' },
  }

  return (
    <Box
      ref={containerRef}
      sx={{
        position: 'relative',
        overflow: 'hidden',
        background: 'linear-gradient(to bottom, rgba(30, 41, 59, 0.3), rgba(15, 23, 42, 0.5))',
        borderRadius: 2,
        ...sizeStyles[size],
      }}
    />
  )
}

export default RainAnimation
