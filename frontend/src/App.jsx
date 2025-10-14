import React, { useState, useEffect } from 'react'
import axios from 'axios'

function App() {
  const [channels, setChannels] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // This will be replaced by your actual API URL
    const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    
    axios.get(`${API_URL}/channels/trending`)
      .then(response => {
        setChannels(response.data)
        setLoading(false)
      })
      .catch(error => {
        console.error('Error fetching channels:', error)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return <div style={{ padding: '20px', textAlign: 'center' }}>Loading YouTube Shorts Analytics...</div>
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>🎬 YouTube Shorts Analytics</h1>
      <p>Discover trending YouTube Shorts channels!</p>
      
      <div style={{ marginTop: '20px' }}>
        <h2>Trending Channels</h2>
        {channels.map(channel => (
          <div key={channel.channel_id} style={{ 
            border: '1px solid #ccc', 
            padding: '15px', 
            margin: '10px 0',
            borderRadius: '8px'
          }}>
            <h3>{channel.name}</h3>
            <p>📊 Subscribers: {channel.subs.toLocaleString()}</p>
            <p>📈 Growth: {(channel.growth_14d * 100).toFixed(1)}%</p>
            <p>⭐ Trend Score: {channel.TrendScore}</p>
            <p>🏷️ Label: {channel.label}</p>
            <p>🔑 Keywords: {channel.top_keywords.join(', ')}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App