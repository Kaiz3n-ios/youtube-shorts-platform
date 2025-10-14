@app.get("/channels/trending")
async def get_trending_channels():
    youtube = YouTubeService()
    
    try:
        # Find emerging viral channels
        print("🔍 Hunting for emerging viral channels...")
        channels = youtube.discover_emerging_channels(max_results=15)
        
        # Filter to only show truly emerging channels
        emerging = [c for c in channels if c.get('is_emerging')]
        
        if emerging:
            print(f"🎯 Found {len(emerging)} emerging viral channels!")
            return emerging
        else:
            return [{
                "name": "Scanning for emerging channels...", 
                "status": "Analyzing recent Shorts data",
                "note": "This may take a few minutes to find channels matching your criteria"
            }]
    except Exception as e:
        print(f"Error: {e}")
        return [{"name": f"API Error: {str(e)}", "error": True}]
