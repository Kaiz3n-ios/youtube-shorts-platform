import requests
import os
from typing import List, Dict, Optional

class YouTubeService:
    def __init__(self):
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            print("⚠️ WARNING: YOUTUBE_API_KEY not found in environment variables!")
    
    def search_channels(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for channels publishing Shorts content"""
        if not self.api_key:
            return [{"name": "API Key Missing", "error": "Add YOUTUBE_API_KEY to environment variables"}]
            
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
            
            channels = []
            for item in data.get('items', []):
                channel_id = item['snippet']['channelId']
                channel_info = self.get_channel_stats(channel_id)
                if channel_info:
                    channels.append(channel_info)
            
            return channels
        except Exception as e:
            print(f"YouTube API Error: {e}")
            return [{"name": f"YouTube API Error: {str(e)}", "error": True}]
    
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
            return {
                'channel_id': channel_id,
                'name': channel['snippet']['title'],
                'description': channel['snippet']['description'],
                'subscriber_count': int(channel['statistics'].get('subscriberCount', 0)),
                'view_count': int(channel['statistics'].get('viewCount', 0)),
                'video_count': int(channel['statistics'].get('videoCount', 0)),
            }
        except Exception as e:
            print(f"Error getting channel stats: {e}")
            return None