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
