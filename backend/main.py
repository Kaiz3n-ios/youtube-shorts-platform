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
        # Search for real Shorts channels
        print("Searching for YouTube Shorts channels...")
        channels = youtube.search_channels("#shorts", max_results=10)
        
        if channels:
            print(f"Found {len(channels)} channels")
            return channels
        else:
            return [{"name": "No channels found yet", "subs": 0, "status": "discovering"}]
    except Exception as e:
        print(f"Error: {e}")
        return [{"name": f"API Error: {str(e)}", "subs": 0, "error": True}]

@app.get("/channels/untapped")
async def get_untapped_channels():
    youtube = YouTubeService()
    
    try:
        # Search for smaller channels
        channels = youtube.search_channels("shorts", max_results=10)
        
        if channels:
            # Filter for smaller channels (under 50k subs)
            small_channels = [c for c in channels if c.get('subscriber_count', 0) < 50000]
            return small_channels if small_channels else [{"name": "No untapped channels found", "subs": 0}]
        else:
            return [{"name": "Searching for untapped channels...", "subs": 0}]
    except Exception as e:
        return [{"name": f"Error: {str(e)}", "subs": 0}]

@app.get("/test-youtube")
async def test_youtube_api():
    """Test endpoint to check if YouTube API is working"""
    youtube = YouTubeService()
    
    try:
        # Simple test - search for one channel
        channels = youtube.search_channels("#shorts", max_results=1)
        
        if channels and not channels[0].get('error'):
            return {
                "status": "SUCCESS! YouTube API is working!",
                "channels_found": len(channels),
                "sample_channel": channels[0]['name'],
                "subscribers": channels[0]['subscriber_count']
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
