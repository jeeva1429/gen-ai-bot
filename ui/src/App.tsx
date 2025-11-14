import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import {ThemeProvider,createTheme} from "@mui/material/styles"
import { CssBaseline } from '@mui/material'
import './App.css'
import ChatApp from './components/ChatUI'

function App() {
  const theme =createTheme()
  return (
    <>
     <ThemeProvider theme={theme}>
      <CssBaseline />
      <ChatApp />
    </ThemeProvider>
    </>
  )
}

export default App
