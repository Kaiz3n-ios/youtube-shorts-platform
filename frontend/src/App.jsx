import React, { useState, useEffect } from 'react'
import axios from 'axios'

function App() {
  const [channels, setChannels] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const API_URL = import.meta.env.VITE_API_BASE_URL || 'https://youtube-shorts-platform.onrender.com'
    
    console.log('API URL:', API_URL)
    
    axios.get(`${API_URL}/channels/trending`)
      .then(response => {
        console.log('API Response:', response.data)
        const data = response.data
        
        // Handle both response formats
        if (data.channels !== undefined) {
          // New format: {status, message, channels}
          setChannels(data.channels || [])
          if (data.status === 'error') {
            setError(data.message)
          } else if (data.status === 'no_results') {
            setError(data.message)
          }
        } else if (Array.isArray(data)) {
          // Old format: direct array
          setChannels(data)
        } else {
          setError('Invalid response format from server')
        }
        setLoading(false)
      })
      .catch(error => {
        console.error('Error fetching channels:', error)
        setError('Failed to connect to server. Please try again later.')
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div style={{ 
        padding: '40px', 
        textAlign: 'center', 
        fontFamily: 'Arial, sans-serif',
        backgroundColor: '#f5f5f5',
        minHeight: '100vh'
      }}>
        <h1 style={{ color: '#333' }}>🎬 YouTube Shorts Analytics</h1>
        <div style={{ 
          marginTop: '20px', 
          padding: '20px',
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <p>Loading YouTube Shorts channels...</p>
          <div style={{
            width: '50px',
            height: '50px',
            border: '3px solid #f3f3f3',
            borderTop: '3px solid #3498db',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '20px auto'
          }}></div>
        </div>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ 
        padding: '40px', 
        textAlign: 'center', 
        fontFamily: 'Arial, sans-serif',
        backgroundColor: '#f5f5f5',
        minHeight: '100vh'
      }}>
        <h1 style={{ color: '#333' }}>🎬 YouTube Shorts Analytics</h1>
        <div style={{ 
          marginTop: '20px', 
          padding: '20px',
          backgroundColor: '#ffebee',
          borderRadius: '8px',
          border: '1px solid #f44336',
          color: '#c62828'
        }}>
          <h3>⚠️ Error Loading Data</h3>
          <p>{error}</p>
          <button 
            onClick={() => window.location.reload()}
            style={{
              padding: '10px 20px',
              backgroundColor: '#2196f3',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              marginTop: '10px'
            }}
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div style={{ 
      padding: '20px', 
      fontFamily: 'Arial, sans-serif',
      backgroundColor: '#f5f5f5',
      minHeight: '100vh'
    }}>
      <header style={{ 
        textAlign: 'center', 
        marginBottom: '30px',
        padding: '20px',
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <h1 style={{ color: '#333', margin: 0 }}>🎬 YouTube Shorts Analytics</h1>
        <p style={{ color: '#666', margin: '10px 0 0 0' }}>
          Discover emerging YouTube Shorts channels with viral potential!
        </p>
      </header>
      
      <main>
        <div style={{ 
          backgroundColor: 'white',
          borderRadius: '8px',
          padding: '20px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ color: '#333', marginBottom: '20px' }}>
            Trending Channels ({channels.length} found)
          </h2>
          
          {channels.length === 0 ? (
            <div style={{ 
              textAlign: 'center', 
              padding: '40px',
              color: '#666'
            }}>
              <p>No channels found matching the criteria.</p>
              <p style={{ fontSize: '14px', marginTop: '10px' }}>
                Criteria: 3+ viral videos (1M+ views) in last 10 uploads within 3 months
              </p>
            </div>
          ) : (
            <div style={{ display: 'grid', gap: '15px' }}>
              {channels.map((channel, index) => (
                <div 
                  key={channel.channel_id || index} 
                  style={{ 
                    border: '1px solid #e0e0e0', 
                    padding: '20px', 
                    borderRadius: '8px',
                    backgroundColor: '#fafafa'
                  }}
                >
                  <h3 style={{ 
                    color: '#1976d2', 
                    margin: '0 0 10px 0',
                    fontSize: '18px'
                  }}>
                    {channel.name}
                  </h3>
                  
                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
                    gap: '10px',
                    fontSize: '14px'
                  }}>
                    <div>
                      <strong>📊 Subscribers:</strong> {channel.subscriber_count?.toLocaleString() || 'N/A'}
                    </div>
                    <div>
                      <strong>👀 Total Views:</strong> {channel.view_count?.toLocaleString() || 'N/A'}
                    </div>
                    <div>
                      <strong>🎬 Videos:</strong> {channel.video_count?.toLocaleString() || 'N/A'}
                    </div>
                    <div>
                      <strong>📅 Channel Age:</strong> {channel.channel_age_days ? `${channel.channel_age_days} days` : 'N/A'}
                    </div>
                  </div>
                  
                  {channel.viral_video_count !== undefined && (
                    <div style={{ 
                      marginTop: '10px',
                      padding: '8px',
                      backgroundColor: '#e8f5e8',
                      borderRadius: '4px',
                      fontSize: '14px'
                    }}>
                      <strong>🔥 Viral Videos:</strong> {channel.viral_video_count} recent videos with 500K+ views
                    </div>
                  )}
                  
                  {channel.note && (
                    <div style={{ 
                      marginTop: '8px',
                      fontSize: '12px',
                      color: '#666',
                      fontStyle: 'italic'
                    }}>
                      {channel.note}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
      
      <footer style={{ 
        textAlign: 'center', 
        marginTop: '30px',
        padding: '20px',
        color: '#666',
        fontSize: '14px'
      }}>
        <p>Data provided by YouTube Data API v3 | Searching for channels with viral potential</p>
      </footer>
    </div>
  )
}

export default App
