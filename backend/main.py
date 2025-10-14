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
        print("🔍 Starting channel discovery...")
        result = youtube.discover_emerging_channels(max_results=5)
        
        # Ensure consistent response format
        if isinstance(result, dict):
            return result
        elif isinstance(result, list):
            return {
                "status": "success",
                "message": f"Found {len(result)} channels",
                "channels": result
            }
        else:
            return {
                "status": "error", 
                "message": "Invalid response format from YouTube service",
                "channels": []
            }
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return {
            "status": "error",
            "message": f"System error: {str(e)}", 
            "channels": []
        }

@app.get("/channels/untapped")
async def get_untapped_channels():
    youtube = YouTubeService()
    
    try:
        result = youtube.discover_emerging_channels(max_results=5)
        
        if isinstance(result, dict):
            return result
        else:
            return {
                "status": "success",
                "message": "Untapped channels search",
                "channels": result if isinstance(result, list) else []
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error: {str(e)}",
            "channels": []
        }

@app.get("/test-youtube")
async def test_youtube_api():
    """Test endpoint to check if YouTube API is working"""
    youtube = YouTubeService()
    
    try:
        result = youtube.discover_emerging_channels(max_results=1)
        
        if isinstance(result, dict):
            return result
        else:
            return {
                "status": "success",
                "message": "API test completed",
                "channels": result if isinstance(result, list) else []
            }
            
    except Exception as e:
        return {
            "status": "error", 
            "message": f"YouTube API error: {str(e)}",
            "channels": []
        }

@app.get("/test-format")
async def test_format():
    """Test consistent response format"""
    return {
        "status": "success",
        "message": "Format test successful", 
        "channels": [
            {
                "name": "Test Channel",
                "subscriber_count": 10000,
                "view_count": 500000,
                "video_count": 25,
                "status": "test_data"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
