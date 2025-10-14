// Add this to your channel display component:
<div style={{ 
  display: 'grid', 
  gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', 
  gap: '8px',
  marginTop: '10px',
  fontSize: '12px'
}}>
  <div style={{ padding: '5px', background: '#e3f2fd', borderRadius: '4px' }}>
    <strong>🎯 Potential Score:</strong> {channel.potential_score}/10
  </div>
  <div style={{ padding: '5px', background: '#f3e5f5', borderRadius: '4px' }}>
    <strong>📈 Viral Videos:</strong> {channel.viral_video_count}
  </div>
  <div style={{ padding: '5px', background: '#e8f5e8', borderRadius: '4px' }}>
    <strong>🚀 Growth Velocity:</strong> {channel.growth_velocity?.toFixed(2)}
  </div>
  <div style={{ padding: '5px', background: '#fff3e0', borderRadius: '4px' }}>
    <strong>⭐ Quality Score:</strong> {channel.quality_score}/10
  </div>
  <div style={{ padding: '5px', background: '#fce4ec', borderRadius: '4px' }}>
    <strong>🏷️ Niche:</strong> {channel.niche}
  </div>
</div>
