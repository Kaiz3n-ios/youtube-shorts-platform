from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from services.youtube_service import YouTubeService

app = FastAPI(title="YouTube Shorts Analytics")

# Allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "YouTube Shorts API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/channels/trending")
async def get_trending_channels():
    youtube = YouTubeService()
    
    try:
        # Find emerging viral channels with enhanced discovery
        print("🔍 Multi-niche hunting for emerging viral channels...")
        channels = youtube.discover_emerging_channels(max_results=15)
        
        # Filter to only show truly emerging channels
        emerging = [c for c in channels if c.get('is_emerging')]
        
        if emerging:
            print(f"🎯 Found {len(emerging)} emerging viral channels!")
            return emerging
        else:
            return [{
                "name": "Scanning for emerging channels...", 
                "status": "Analyzing recent Shorts data across multiple niches",
                "note": "This may take a few minutes to find channels matching your criteria"
            }]
    except Exception as e:
        print(f"Error: {e}")
        return [{"name": f"API Error: {str(e)}", "error": True}]

@app.get("/channels/untapped")
async def get_untapped_channels():
    youtube = YouTubeService()
    
    try:
        # Search for smaller channels
        channels = youtube.discover_emerging_channels(max_results=10)
        
        # Filter for smaller channels (under 100k subs)
        small_channels = [c for c in channels if c.get('subscriber_count', 0) < 100000]
        return small_channels if small_channels else [{"name": "No untapped channels found", "subs": 0}]
    except Exception as e:
        return [{"name": f"Error: {str(e)}", "subs": 0}]

@app.get("/test-youtube")
async def test_youtube_api():
    """Test endpoint to check if YouTube API is working"""
    youtube = YouTubeService()
    
    try:
        # Simple test - search for emerging channels
        channels = youtube.discover_emerging_channels(max_results=1)
        
        if channels and not channels[0].get('error'):
            return {
                "status": "SUCCESS! Enhanced YouTube API is working!",
                "channels_found": len(channels),
                "sample_channel": channels[0]['name'],
                "potential_score": channels[0].get('potential_score', 'N/A'),
                "niche": channels[0].get('niche', 'N/A')
            }
        elif channels and channels[0].get('error'):
            return {
                "status": "YouTube API Error",
                "error": channels[0]['name']
            }
        else:
            return {"status": "No channels found but API is responding"}
            
    except Exception as e:
        return {"status": f"YouTube API error: {str(e)}"}

@app.get("/niches")
async def get_available_niches():
    """Get list of available niches for discovery"""
    youtube = YouTubeService()
    return {
        "available_niches": list(youtube.NICHE_KEYWORDS.keys()),
        "total_niches": len(youtube.NICHE_KEYWORDS)
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
