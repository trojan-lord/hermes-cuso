import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

// Import Astryx CSS (order matters)
import '@astryxdesign/core/astryx.css'
import '@astryxdesign/theme-neutral/theme.css'
import '@astryxdesign/core/reset.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
