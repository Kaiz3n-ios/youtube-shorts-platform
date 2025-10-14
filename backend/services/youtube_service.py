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
            print("❌ YOUTUBE_API_KEY not found in environment variables!")
        else:
            print("✅ YouTube API Key loaded successfully")
    
    def discover_emerging_channels(self, max_results: int = 20) -> List[Dict]:
        """Discover emerging channels with viral Shorts"""
        if not self.api_key:
            return [{"error": "API Key missing"}]
        
        print("🔍 Hunting for emerging viral channels...")
        
        # Search for recent Shorts content
        search_results = self._search_recent_shorts(max_results * 2)  # Get more to filter
        
        emerging_channels = []
        
        for video in search_results:
            try:
                channel_id = video['channel_id']
                
                # Skip if we already processed this channel
                if any(c['channel_id'] == channel_id for c in emerging_channels):
                    continue
                
                print(f"🔎 Analyzing channel: {video['channel_title']}")
                
                # Get channel details and recent videos
                channel_analysis = self._analyze_channel_potential(channel_id)
                
                if channel_analysis and self._is_emerging_channel(channel_analysis):
                    print(f"🎯 FOUND EMERGING: {channel_analysis['name']}")
                    emerging_channels.append(channel_analysis)
                
                # Rate limiting
                time.sleep(0.2)
                
                if len(emerging_channels) >= max_results:
                    break
                    
            except Exception as e:
                print(f"❌ Error analyzing channel: {e}")
                continue
        
        print(f"✅ Found {len(emerging_channels)} emerging channels")
        return emerging_channels
    
    def _search_recent_shorts(self, max_results: int = 40) -> List[Dict]:
        """Search for recent Shorts videos"""
        url = f"{self.base_url}/search"
        params = {
            'part': 'snippet',
            'q': '#shorts',
            'type': 'video',
            'maxResults': max_results,
            'order': 'date',  # Get newest first
            'publishedAfter': (datetime.utcnow() - timedelta(days=30)).isoformat() + 'Z',
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            videos = []
            for item in data.get('items', []):
                video_data = {
                    'video_id': item['id']['videoId'],
                    'channel_id': item['snippet']['channelId'],
                    'channel_title': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'title': item['snippet']['title']
                }
                videos.append(video_data)
            
            return videos
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def _analyze_channel_potential(self, channel_id: str) -> Optional[Dict]:
        """Analyze if a channel has emerging potential"""
        try:
            # Get channel stats
            channel_stats = self.get_channel_stats(channel_id)
            if not channel_stats:
                return None
            
            # Get recent videos for analysis
            recent_videos = self._get_channel_recent_videos(channel_id, max_results=15)
            
            # Calculate viral metrics
            analysis = self._calculate_viral_metrics(channel_stats, recent_videos)
            
            return analysis
            
        except Exception as e:
            print(f"❌ Channel analysis error: {e}")
            return None
    
    def _get_channel_recent_videos(self, channel_id: str, max_results: int = 15) -> List[Dict]:
        """Get recent videos from a channel"""
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
                video_stats = self._get_video_stats(video_id)
                
                if video_stats:
                    video_data = {
                        'video_id': video_id,
                        'title': item['snippet']['title'],
                        'published_at': item['snippet']['publishedAt'],
                        'view_count': video_stats.get('view_count', 0),
                        'like_count': video_stats.get('like_count', 0)
                    }
                    videos.append(video_data)
            
            return videos
            
        except Exception as e:
            print(f"❌ Recent videos error: {e}")
            return []
    
    def _get_video_stats(self, video_id: str) -> Optional[Dict]:
        """Get video statistics"""
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
                stats = data['items'][0]['statistics']
                return {
                    'view_count': int(stats.get('viewCount', 0)),
                    'like_count': int(stats.get('likeCount', 0)),
                    'comment_count': int(stats.get('commentCount', 0))
                }
            return None
            
        except Exception as e:
            print(f"❌ Video stats error: {e}")
            return None
    
    def _calculate_viral_metrics(self, channel_stats: Dict, recent_videos: List[Dict]) -> Dict:
        """Calculate if channel meets viral criteria"""
        # Sort videos by publish date (newest first)
        recent_videos.sort(key=lambda x: x['published_at'], reverse=True)
        
        # Take last 10 videos
        last_10_videos = recent_videos[:10] if len(recent_videos) >= 10 else recent_videos
        
        # Count viral videos (1M+ views)
        viral_count = sum(1 for video in last_10_videos if video['view_count'] >= 1000000)
        
        # Calculate average views for last 10 videos
        total_views = sum(video['view_count'] for video in last_10_videos)
        avg_views = total_views / len(last_10_videos) if last_10_videos else 0
        
        # Check channel age (approximate)
        channel_age = self._estimate_channel_age(recent_videos)
        
        analysis = {
            **channel_stats,
            'viral_video_count': viral_count,
            'total_viral_views': sum(video['view_count'] for video in last_10_videos if video['view_count'] >= 1000000),
            'avg_recent_views': avg_views,
            'recent_videos_analyzed': len(last_10_videos),
            'channel_age_estimate': channel_age,
            'is_emerging': viral_count >= 3 and channel_age <= 90  # 3 months
        }
        
        return analysis
    
    def _estimate_channel_age(self, videos: List[Dict]) -> int:
        """Estimate channel age in days based on video publish dates"""
        if not videos:
            return 365  # Default to 1 year if no data
        
        publish_dates = [datetime.fromisoformat(v['published_at'].replace('Z', '')) for v in videos]
        oldest_video = min(publish_dates)
        days_old = (datetime.utcnow() - oldest_video).days
        
        return min(days_old, 365)  # Cap at 1 year
    
    def _is_emerging_channel(self, analysis: Dict) -> bool:
        """Check if channel meets emerging criteria"""
        return (
            analysis['is_emerging'] and
            analysis['viral_video_count'] >= 3 and
            analysis['subscriber_count'] < 500000  # Under 500K subscribers
        )
    
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
            
            return channel_data
            
        except Exception as e:
            print(f"❌ Channel stats error: {e}")
            return None
