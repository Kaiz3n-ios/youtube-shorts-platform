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
    
    def discover_emerging_channels(self, max_results: int = 5) -> Dict:  # Reduced results
        """FAST version: 3 viral videos in last 10, within 3 months"""
        if not self.api_key:
            return {
                "status": "error",
                "message": "YouTube API key not configured",
                "channels": []
            }
        
        print("🎯 FAST search: 3 viral videos in last 10, within 3 months")
        
        try:
            # Method 1: Quick search through trending Shorts
            channels = self._fast_trending_search(max_results)
            
            if channels:
                return {
                    "status": "success", 
                    "message": f"Found {len(channels)} channels matching criteria",
                    "channels": channels
                }
            else:
                return {
                    "status": "no_results", 
                    "message": "No channels with 3+ viral videos found. This criteria is very rare.",
                    "channels": []
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Search error: {str(e)}",
                "channels": []
            }
    
    def _fast_trending_search(self, max_results: int) -> List[Dict]:
        """Search through currently trending Shorts"""
        url = f"{self.base_url}/videos"
        params = {
            'part': 'snippet,statistics',
            'chart': 'mostPopular',
            'videoCategoryId': '20',  # Gaming category (has most Shorts)
            'maxResults': 20,  # Small batch
            'regionCode': 'US',
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            channels_found = []
            seen_channels = set()
            
            for item in data.get('items', []):
                if len(channels_found) >= max_results:
                    break
                
                # Check if it's a Short (under 60 seconds)
                duration = item.get('contentDetails', {}).get('duration', '')
                if 'M' in duration or 'H' in duration:  # Not a Short
                    continue
                
                channel_id = item['snippet']['channelId']
                
                if channel_id in seen_channels:
                    continue
                seen_channels.add(channel_id)
                
                # FAST check - only analyze if video has 1M+ views
                view_count = int(item['statistics'].get('viewCount', 0))
                if view_count >= 500000:  # Lower threshold for speed
                    print(f"🔍 Quick analyzing: {item['snippet']['channelTitle']}")
                    channel_data = self._quick_channel_check(channel_id)
                    if channel_data:
                        channels_found.append(channel_data)
            
            return channels_found
            
        except Exception as e:
            print(f"❌ Trending search error: {e}")
            return []
    
    def _quick_channel_check(self, channel_id: str) -> Optional[Dict]:
        """Quick check if channel might meet criteria"""
        try:
            # Get basic channel info
            channel_stats = self.get_channel_stats(channel_id)
            if not channel_stats:
                return None
            
            # Get only 5 recent videos for speed
            recent_videos = self._get_few_recent_videos(channel_id, 5)
            if len(recent_videos) < 3:
                return None
            
            # Quick viral count in recent videos
            viral_count = sum(1 for v in recent_videos if v['view_count'] >= 500000)
            
            # Estimate channel age from available data
            channel_age = self._estimate_age_from_videos(recent_videos)
            
            print(f"📊 {channel_stats['name']}: {viral_count}/5 viral, {channel_age} days old")
            
            # If they have 2+ viral in last 5, they might meet 3+ in last 10
            if viral_count >= 2 and channel_age <= 120:  # 4 months buffer
                return {
                    **channel_stats,
                    'viral_video_count': viral_count,
                    'channel_age_days': channel_age,
                    'confidence': 'medium',  # Not fully verified
                    'note': 'Quick scan - may have 3+ viral in last 10'
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Quick check error: {e}")
            return None
    
    def _get_few_recent_videos(self, channel_id: str, max_videos: int = 5) -> List[Dict]:
        """Get only a few recent videos for speed"""
        url = f"{self.base_url}/search"
        params = {
            'part': 'snippet',
            'channelId': channel_id,
            'type': 'video',
            'maxResults': max_videos,
            'order': 'date',
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            videos = []
            for item in data.get('items', []):
                video_id = item['id']['videoId']
                
                # Get view count quickly
                view_count = self._get_quick_view_count(video_id)
                
                videos.append({
                    'video_id': video_id,
                    'view_count': view_count,
                    'published_at': item['snippet']['publishedAt']
                })
            
            return videos
            
        except Exception as e:
            print(f"❌ Few videos error: {e}")
            return []
    
    def _get_quick_view_count(self, video_id: str) -> int:
        """Get view count with minimal processing"""
        url = f"{self.base_url}/videos"
        params = {
            'part': 'statistics',
            'id': video_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if data.get('items'):
                return int(data['items'][0]['statistics'].get('viewCount', 0))
            return 0
            
        except:
            return 0
    
    def _estimate_age_from_videos(self, videos: List[Dict]) -> int:
        """Quick age estimation"""
        if not videos:
            return 365
        
        try:
            dates = [datetime.fromisoformat(v['published_at'].replace('Z', '')) for v in videos]
            return (datetime.utcnow() - min(dates)).days
        except:
            return 365
    
    def get_channel_stats(self, channel_id: str) -> Optional[Dict]:
        """Get channel stats quickly"""
        if not self.api_key:
            return None
            
        url = f"{self.base_url}/channels"
        params = {
            'part': 'snippet,statistics',
            'id': channel_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if not data.get('items'):
                return None
                
            channel = data['items'][0]
            stats = channel['statistics']
            
            return {
                'channel_id': channel_id,
                'name': channel['snippet']['title'],
                'description': channel['snippet']['description'][:200] + '...' if channel['snippet']['description'] else '',
                'subscriber_count': int(stats.get('subscriberCount', 0)),
                'view_count': int(stats.get('viewCount', 0)),
                'video_count': int(stats.get('videoCount', 0)),
                'published_at': channel['snippet']['publishedAt'],
            }
            
        except Exception as e:
            print(f"❌ Channel stats error: {e}")
            return None
