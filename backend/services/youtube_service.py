import requests
import os
import time
from typing import List, Dict, Optional

class YouTubeService:
    def __init__(self):
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        
        if not self.api_key:
            print("❌ YOUTUBE_API_KEY not found in environment variables!")
        else:
            print("✅ YouTube API Key loaded successfully")
    
    def search_channels(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for channels publishing Shorts content"""
        if not self.api_key:
            return [{
                "name": "API Key Missing", 
                "error": "Add YOUTUBE_API_KEY to Render environment variables",
                "subscriber_count": 0
            }]
            
        print(f"🔍 Searching YouTube for: {query}")
        
        url = f"{self.base_url}/search"
        params = {
            'part': 'snippet',
            'q': f'{query} #shorts',
            'type': 'channel',
            'maxResults': max_results,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'error' in data:
                error_msg = data['error']['message']
                print(f"❌ YouTube API Error: {error_msg}")
                return [{
                    "name": f"YouTube API Error: {error_msg}",
                    "subscriber_count": 0,
                    "error": True
                }]
            
            channels = []
            for item in data.get('items', []):
                channel_id = item['snippet']['channelId']
                print(f"📺 Found channel: {item['snippet']['title']}")
                
                # Get detailed channel info
                channel_info = self.get_channel_stats(channel_id)
                if channel_info:
                    channels.append(channel_info)
                
                # Rate limiting - be nice to YouTube API
                time.sleep(0.1)
            
            print(f"✅ Found {len(channels)} channels with details")
            return channels
            
        except Exception as e:
            print(f"❌ YouTube API Exception: {e}")
            return [{
                "name": f"API Error: {str(e)}", 
                "subscriber_count": 0,
                "error": True
            }]
    
    def get_channel_stats(self, channel_id: str) -> Optional[Dict]:
        """Get detailed channel statistics"""
        if not self.api_key:
            return None
            
        url = f"{self.base_url}/channels"
        params = {
            'part': 'snippet,statistics',
            'id': channel_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if not data.get('items'):
                return None
                
            channel = data['items'][0]
            stats = channel['statistics']
            
            channel_data = {
                'channel_id': channel_id,
                'name': channel['snippet']['title'],
                'description': channel['snippet']['description'][:200] + '...' if channel['snippet']['description'] else '',
                'subscriber_count': int(stats.get('subscriberCount', 0)),
                'view_count': int(stats.get('viewCount', 0)),
                'video_count': int(stats.get('videoCount', 0)),
                'published_at': channel['snippet']['publishedAt'],
            }
            
            print(f"📊 Channel stats: {channel_data['name']} - {channel_data['subscriber_count']} subs")
            return channel_data
            
        except Exception as e:
            print(f"❌ Error getting channel stats for {channel_id}: {e}")
            return None
    
    def test_api_connection(self) -> Dict:
        """Test if YouTube API is working"""
        if not self.api_key:
            return {"status": "error", "message": "No API key found"}
        
        url = f"{self.base_url}/channels"
        params = {
            'part': 'snippet',
            'id': 'UC_x5XG1OV2P6uZZ5FSM9Ttw',  # YouTube's own channel
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'error' in data:
                return {
                    "status": "error", 
                    "message": data['error']['message'],
                    "code": data['error']['code']
                }
            else:
                return {
                    "status": "success", 
                    "message": "YouTube API is working!",
                    "channel": data['items'][0]['snippet']['title'] if data.get('items') else "No data"
                }
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
