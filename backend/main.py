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
        print("🔍 Starting efficient tiered discovery...")
        result = youtube.discover_channels_tiered(max_total=12)
        return result
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"System error: {str(e)}", 
            "channels": [],
            "tier_summary": {"gold": 0, "silver": 0, "bronze": 0}
        }

@app.get("/channels/untapped")
async def get_untapped_channels():
    youtube = YouTubeService()
    
    try:
        result = youtube.discover_channels_tiered(max_total=8)
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error: {str(e)}",
            "channels": [],
            "tier_summary": {"gold": 0, "silver": 0, "bronze": 0}
        }

@app.get("/test-youtube")
async def test_youtube_api():
    """Test endpoint to check if YouTube API is working"""
    youtube = YouTubeService()
    
    try:
        result = youtube.discover_channels_tiered(max_total=3)
        return result
            
    except Exception as e:
        return {
            "status": "error", 
            "message": f"YouTube API error: {str(e)}",
            "channels": [],
            "tier_summary": {"gold": 0, "silver": 0, "bronze": 0}
        }

@app.get("/test-format")
async def test_format():
    """Test consistent response format"""
    return {
        "status": "success",
        "message": "Format test successful", 
        "channels": [
            {
                "name": "Test Channel - Gold Tier",
                "subscriber_count": 15000,
                "view_count": 2500000,
                "video_count": 25,
                "tier": "gold",
                "viral_video_count": 3,
                "criteria": "3+ viral videos in recent content"
            },
            {
                "name": "Test Channel - Silver Tier", 
                "subscriber_count": 8000,
                "view_count": 1200000,
                "video_count": 18,
                "tier": "silver",
                "viral_video_count": 1,
                "criteria": "1 viral video + consistent growth"
            },
            {
                "name": "Test Channel - Bronze Tier",
                "subscriber_count": 5000,
                "view_count": 800000,
                "video_count": 15,
                "tier": "bronze", 
                "growth_score": 7,
                "criteria": "Strong growth trajectory"
            }
        ],
        "tier_summary": {
            "gold": 1,
            "silver": 1,
            "bronze": 1
        },
        "performance": {
            "api_calls": 0,
            "duration_seconds": 0.1,
            "cached_requests": "test_data"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
