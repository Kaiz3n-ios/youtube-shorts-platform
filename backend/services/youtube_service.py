import requests
import os
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class YouTubeService:
    def __init__(self):
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        
        if not self.api_key:
            print("❌ YOUTUBE_API_KEY not found!")
        else:
            print("✅ YouTube API Key loaded")
    
    def discover_emerging_channels(self, max_results: int = 10) -> Dict:
        """EXACT: 3 viral videos in last 10, within 3 months"""
        if not self.api_key:
            return {
                "status": "error",
                "message": "YouTube API key not configured",
                "channels": []
            }
        
        print("🎯 Searching for EXACT criteria: 3 viral videos in last 10, within 3 months")
        
        try:
            channels = self._exact_viral_search(max_results)
            
            if channels:
                return {
                    "status": "success", 
                    "message": f"Found {len(channels)} channels matching exact criteria",
                    "channels": channels
                }
            else:
                return {
                    "status": "no_results",
                    "message": "No channels found with 3+ viral videos in last 10 uploads within 3 months",
                    "channels": []
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"YouTube API error: {str(e)}",
                "channels": []
            }
    
    def _exact_viral_search(self, max_results: int) -> List[Dict]:
        """Find channels with exactly 3+ viral videos in last 10 within 3 months"""
        # Search for recent viral Shorts
        viral_videos = self._find_recent_viral_shorts(max_results * 5)
        
        channels_found = []
        seen_channels = set()
        
        for video in viral_videos:
            if len(channels_found) >= max_results:
                break
                
            channel_id = video['channel_id']
            
            if channel_id in seen_channels:
                continue
            seen_channels.add(channel_id)
            
            print(f"🔍 Analyzing channel: {video['channel_title']}")
            
            # Check if channel meets EXACT criteria
            channel_data = self._check_exact_criteria(channel_id)
            if channel_data:
                channels_found.append(channel_data)
                print(f"🎯 FOUND MATCH: {channel_data['name']}")
            
            time.sleep(0.2)
        
        return channels_found
    
    def _find_recent_viral_shorts(self, max_videos: int) -> List[Dict]:
        """Find recent Shorts with 1M+ views"""
        url = f"{self.base_url}/search"
        params = {
            'part': 'snippet',
            'q': '#shorts',
            'type': 'video',
            'maxResults': min(50, max_videos),
            'order': 'viewCount',  # Get most viewed first
            'publishedAfter': (datetime.utcnow() - timedelta(days=90)).isoformat() + 'Z',
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            viral_videos = []
            for item in data.get('items', []):
                video_id = item['id']['videoId']
                
                # Check if video actually has 1M+ views
                view_count = self._get_video_view_count(video_id)
                if view_count >= 1000000:
                    viral_videos.append({
                        'video_id': video_id,
                        'channel_id': item['snippet']['channelId'],
                        'channel_title': item['snippet']['channelTitle'],
                        'view_count': view_count,
                        'published_at': item['snippet']['publishedAt']
                    })
                
                if len(viral_videos) >= max_videos:
                    break
            
            print(f"📊 Found {len(viral_videos)} viral Shorts to analyze")
            return viral_videos
            
        except Exception as e:
            print(f"❌ Viral search error: {e}")
            return []
    
    def _check_exact_criteria(self, channel_id: str) -> Optional[Dict]:
        """Check if channel meets EXACT 3-viral-in-10 criteria"""
        try:
            # Get channel info
            channel_stats = self.get_channel_stats(channel_id)
            if not channel_stats:
                return None
            
            # Get last 15 videos (to ensure we have 10 recent ones)
            recent_videos = self._get_channel_recent_videos(channel_id, 15)
            if len(recent_videos) < 10:
                return None  # Not enough content
            
            # Check channel age (started within 3 months)
            channel_age = self._get_channel_age(recent_videos)
            if channel_age > 90:  # More than 3 months
                return None
            
            # Count viral videos in last 10
            last_10_videos = recent_videos[:10]
            viral_count = sum(1 for video in last_10_videos if video['view_count'] >= 1000000)
            
            print(f"📈 Channel {channel_stats['name']}: {viral_count}/10 viral videos, {channel_age} days old")
            
            if viral_count >= 3:
                return {
                    **channel_stats,
                    'viral_video_count': viral_count,
                    'channel_age_days': channel_age,
                    'total_recent_views': sum(v['view_count'] for v in last_10_videos),
                    'avg_recent_views': sum(v['view_count'] for v in last_10_videos) / 10,
                    'exact_match': True,
                    'criteria_met': f"3+ viral videos in last 10 uploads within {channel_age} days"
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Criteria check error: {e}")
            return None
    
    def _get_channel_age(self, videos: List[Dict]) -> int:
        """Calculate channel age from oldest video"""
        if not videos:
            return 365
        
        publish_dates = [datetime.fromisoformat(v['published_at'].replace('Z', '')) for v in videos]
        oldest_video = min(publish_dates)
        days_old = (datetime.utcnow() - oldest_video).days
        
        return days_old
    
    def _get_channel_recent_videos(self, channel_id: str, max_results: int = 15) -> List[Dict]:
        """Get recent videos from channel"""
        url = f"{self.base_url}/search"
        params = {
            'part': 'snippet',
            'channelId': channel_id,
            'type': 'video',
            'maxResults': max_results,
            'order': 'date',
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            videos = []
            for item in data.get('items', []):
                video_id = item['id']['videoId']
                view_count = self._get_video_view_count(video_id)
                
                videos.append({
                    'video_id': video_id,
                    'title': item['snippet']['title'],
                    'view_count': view_count,
                    'published_at': item['snippet']['publishedAt']
                })
            
            return videos
            
        except Exception as e:
            print(f"❌ Recent videos error: {e}")
            return []
    
    def _get_video_view_count(self, video_id: str) -> int:
        """Get video view count"""
        url = f"{self.base_url}/videos"
        params = {
            'part': 'statistics',
            'id': video_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('items'):
                return int(data['items'][0]['statistics'].get('viewCount', 0))
            return 0
            
        except Exception as e:
            print(f"❌ View count error: {e}")
            return 0
    
    def get_channel_stats(self, channel_id: str) -> Optional[Dict]:
        """Get channel statistics"""
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
            
            return {
                'channel_id': channel_id,
                'name': channel['snippet']['title'],
                'description': channel['snippet']['description'],
                'subscriber_count': int(stats.get('subscriberCount', 0)),
                'view_count': int(stats.get('viewCount', 0)),
                'video_count': int(stats.get('videoCount', 0)),
                'published_at': channel['snippet']['publishedAt'],
            }
            
        except Exception as e:
            print(f"❌ Channel stats error: {e}")
            return None
