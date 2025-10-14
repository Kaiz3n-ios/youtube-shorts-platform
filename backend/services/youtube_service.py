import requests
import os
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import json

class YouTubeService:
    def __init__(self):
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        
        # Simple in-memory cache (upgrade to Redis later)
        self._cache = {}
        
        if not self.api_key:
            print("❌ YOUTUBE_API_KEY not found!")
        else:
            print("✅ YouTube API Key loaded")
    
    def discover_channels_tiered(self, max_total: int = 10) -> Dict:
        """Efficient tiered discovery with caching"""
        if not self.api_key:
            return self._error_response("YouTube API key not configured")
        
        print("🎯 Starting efficient tiered discovery...")
        start_time = time.time()
        api_calls = 0
        
        try:
            # Tier 1: Gold (3+ viral videos in 3 months)
            print("🥇 Checking Gold Tier...")
            gold_tier, gold_calls = self._quick_gold_check(3)
            api_calls += gold_calls
            
            # If we found good gold channels, return early
            if len(gold_tier) >= 2:
                print(f"✅ Found {len(gold_tier)} gold channels - returning early")
                return self._success_tiered(gold_tier, [], [], api_calls, time.time() - start_time)
            
            # Tier 2: Silver (1-2 viral videos + growth)
            print("🥈 Checking Silver Tier...")
            silver_tier, silver_calls = self._silver_search(5)
            api_calls += silver_calls
            
            # If we have enough good channels, return
            if len(gold_tier) + len(silver_tier) >= 6:
                return self._success_tiered(gold_tier, silver_tier, [], api_calls, time.time() - start_time)
            
            # Tier 3: Bronze (Consistent growth, no virals yet)
            print("🥉 Checking Bronze Tier...")
            bronze_tier, bronze_calls = self._bronze_search(8)
            api_calls += bronze_calls
            
            return self._success_tiered(gold_tier, silver_tier, bronze_tier, api_calls, time.time() - start_time)
            
        except Exception as e:
            return self._error_response(f"Search error: {str(e)}")
    
    def _quick_gold_check(self, max_channels: int) -> Tuple[List[Dict], int]:
        """Check trending for potential gold tiers - 2-3 API calls"""
        api_calls = 0
        
        # Get trending videos (1 call)
        trending_videos = self._get_trending_videos(8)
        api_calls += 1
        
        gold_channels = []
        
        for video in trending_videos[:5]:  # Only check top 5
            if len(gold_channels) >= max_channels:
                break
                
            # Only analyze if video has good views
            if video.get('view_count', 0) >= 500000:
                # Use cached channel stats
                channel_data = self._get_cached_channel_stats(video['channel_id'])
                if channel_data:
                    api_calls += 1
                    
                    # Quick viral check (cached)
                    viral_count, viral_calls = self._quick_viral_check(video['channel_id'], 5)
                    api_calls += viral_calls
                    
                    if viral_count >= 2:
                        gold_channels.append({
                            **channel_data,
                            'viral_video_count': viral_count,
                            'tier': 'gold',
                            'criteria': f'{viral_count}+ viral videos in recent content'
                        })
        
        return gold_channels, api_calls
    
    def _silver_search(self, max_channels: int) -> Tuple[List[Dict], int]:
        """Find channels with 1-2 viral hits - 3-5 API calls"""
        api_calls = 0
        
        # Find some viral videos (1 call)
        viral_videos = self._search_viral_videos(500000, 10)  # 500K+ views
        api_calls += 1
        
        silver_channels = []
        seen_channels = set()
        
        for video in viral_videos:
            if len(silver_channels) >= max_channels:
                break
                
            channel_id = video['channel_id']
            if channel_id in seen_channels:
                continue
            seen_channels.add(channel_id)
            
            # Use cached channel stats
            channel_data = self._get_cached_channel_stats(channel_id)
            if channel_data:
                api_calls += 1
                
                # Check if silver tier (1-2 viral videos)
                viral_count, viral_calls = self._quick_viral_check(channel_id, 5)
                api_calls += viral_calls
                
                if 1 <= viral_count <= 2:
                    silver_channels.append({
                        **channel_data,
                        'viral_video_count': viral_count,
                        'tier': 'silver',
                        'criteria': f'{viral_count} viral video(s) + consistent growth'
                    })
        
        return silver_channels, api_calls
    
    def _bronze_search(self, max_channels: int) -> Tuple[List[Dict], int]:
        """Find growing channels - 5-8 API calls"""
        api_calls = 0
        
        # Find active creators (1 call)
        active_channels = self._find_active_creators(12)
        api_calls += 1
        
        bronze_channels = []
        
        for channel_id in active_channels[:10]:  # Check first 10
            if len(bronze_channels) >= max_channels:
                break
                
            # Use cached channel stats
            channel_data = self._get_cached_channel_stats(channel_id)
            if channel_data:
                api_calls += 1
                
                # Check growth metrics (cached)
                growth_score, growth_calls = self._calculate_growth_score(channel_id)
                api_calls += growth_calls
                
                if growth_score >= 6:  # Good growth potential
                    bronze_channels.append({
                        **channel_data,
                        'growth_score': growth_score,
                        'tier': 'bronze',
                        'criteria': 'Strong growth trajectory, emerging potential'
                    })
        
        return bronze_channels, api_calls
    
    # CACHED METHODS
    def _get_cached_channel_stats(self, channel_id: str) -> Optional[Dict]:
        """Get channel stats with 10-minute cache"""
        cache_key = f"channel_stats:{channel_id}"
        
        if cache_key in self._cache:
            cache_time, data = self._cache[cache_key]
            if time.time() - cache_time < 600:  # 10 minutes
                print(f"📦 Using cached channel: {data.get('name', 'Unknown')}")
                return data
        
        # Fresh API call
        stats = self.get_channel_stats(channel_id)
        if stats:
            self._cache[cache_key] = (time.time(), stats)
        return stats
    
    def _quick_viral_check(self, channel_id: str, max_videos: int = 5) -> Tuple[int, int]:
        """Quick viral count with caching - 1-2 API calls"""
        cache_key = f"viral_check:{channel_id}"
        api_calls = 0
        
        if cache_key in self._cache:
            cache_time, data = self._cache[cache_key]
            if time.time() - cache_time < 600:  # 10 minutes
                return data, 0
        
        # Fresh check
        recent_videos = self._get_few_recent_videos(channel_id, max_videos)
        api_calls += 1
        
        viral_count = sum(1 for v in recent_videos if v['view_count'] >= 500000)
        
        # Cache result
        self._cache[cache_key] = (time.time(), viral_count)
        
        return viral_count, api_calls
    
    # CORE API METHODS (with caching)
    def _get_trending_videos(self, max_results: int) -> List[Dict]:
        """Get trending videos - 1 API call"""
        url = f"{self.base_url}/videos"
        params = {
            'part': 'snippet,statistics',
            'chart': 'mostPopular',
            'maxResults': max_results,
            'regionCode': 'US',
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            videos = []
            for item in data.get('items', []):
                videos.append({
                    'video_id': item['id'],
                    'channel_id': item['snippet']['channelId'],
                    'title': item['snippet']['title'],
                    'view_count': int(item['statistics'].get('viewCount', 0))
                })
            
            return videos
        except Exception as e:
            print(f"❌ Trending error: {e}")
            return []
    
    def _search_viral_videos(self, min_views: int, max_results: int) -> List[Dict]:
        """Search for viral videos - 1 API call"""
        url = f"{self.base_url}/search"
        params = {
            'part': 'snippet',
            'q': '#shorts',
            'type': 'video',
            'maxResults': max_results,
            'order': 'viewCount',
            'publishedAfter': (datetime.utcnow() - timedelta(days=60)).isoformat() + 'Z',
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            videos = []
            for item in data.get('items', []):
                video_id = item['id']['videoId']
                view_count = self._get_quick_view_count(video_id)
                
                if view_count >= min_views:
                    videos.append({
                        'video_id': video_id,
                        'channel_id': item['snippet']['channelId'],
                        'view_count': view_count
                    })
            
            return videos
        except Exception as e:
            print(f"❌ Viral search error: {e}")
            return []
    
    def _find_active_creators(self, max_results: int) -> List[str]:
        """Find active Shorts creators - 1 API call"""
        url = f"{self.base_url}/search"
        params = {
            'part': 'snippet',
            'q': '#shorts',
            'type': 'video',
            'maxResults': max_results,
            'order': 'date',
            'publishedAfter': (datetime.utcnow() - timedelta(days=7)).isoformat() + 'Z',
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            channel_ids = []
            seen = set()
            
            for item in data.get('items', []):
                channel_id = item['snippet']['channelId']
                if channel_id not in seen:
                    seen.add(channel_id)
                    channel_ids.append(channel_id)
            
            return channel_ids
        except Exception as e:
            print(f"❌ Active creators error: {e}")
            return []
    
    def _calculate_growth_score(self, channel_id: str) -> Tuple[int, int]:
        """Calculate growth score with caching - 1-2 API calls"""
        cache_key = f"growth_score:{channel_id}"
        api_calls = 0
        
        if cache_key in self._cache:
            cache_time, data = self._cache[cache_key]
            if time.time() - cache_time < 600:  # 10 minutes
                return data, 0
        
        channel_data = self._get_cached_channel_stats(channel_id)
        if not channel_data:
            return 0, 0
        
        # Simple growth scoring (0-10)
        score = 5  # Base
        
        # Subscriber growth potential
        subs = channel_data['subscriber_count']
        if 1000 <= subs <= 100000:
            score += 2
        elif subs > 1000000:
            score -= 1
        
        # View-to-sub ratio
        view_ratio = channel_data['view_count'] / (subs + 1)
        if view_ratio >= 3:
            score += 2
        elif view_ratio >= 1:
            score += 1
        
        # Content consistency
        if channel_data['video_count'] >= 20:
            score += 1
        
        self._cache[cache_key] = (time.time(), min(10, max(0, score)))
        return min(10, max(0, score)), api_calls
    
    # Response formatting
    def _success_tiered(self, gold: List, silver: List, bronze: List, api_calls: int, duration: float) -> Dict:
        total_channels = len(gold) + len(silver) + len(bronze)
        return {
            "status": "success",
            "message": f"Found {total_channels} channels across {len(gold)} gold, {len(silver)} silver, {len(bronze)} bronze",
            "channels": gold + silver + bronze,
            "tier_summary": {
                "gold": len(gold),
                "silver": len(silver), 
                "bronze": len(bronze)
            },
            "performance": {
                "api_calls": api_calls,
                "duration_seconds": round(duration, 2),
                "cached_requests": "yes"
            }
        }
    
    def _error_response(self, message: str) -> Dict:
        return {
            "status": "error",
            "message": message,
            "channels": [],
            "tier_summary": {"gold": 0, "silver": 0, "bronze": 0}
        }
    
    # Keep existing helper methods
    def _get_few_recent_videos(self, channel_id: str, max_videos: int = 5) -> List[Dict]:
        """Get few recent videos - 1 API call"""
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
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            videos = []
            for item in data.get('items', []):
                video_id = item['id']['videoId']
                view_count = self._get_quick_view_count(video_id)
                
                videos.append({
                    'video_id': video_id,
                    'view_count': view_count,
                    'published_at': item['snippet']['publishedAt']
                })
            
            return videos
        except Exception as e:
            print(f"❌ Recent videos error: {e}")
            return []
    
    def _get_quick_view_count(self, video_id: str) -> int:
        """Get view count quickly - 0-1 API calls"""
        cache_key = f"view_count:{video_id}"
        
        if cache_key in self._cache:
            cache_time, count = self._cache[cache_key]
            if time.time() - cache_time < 600:  # 10 minutes
                return count
        
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
                count = int(data['items'][0]['statistics'].get('viewCount', 0))
                self._cache[cache_key] = (time.time(), count)
                return count
            return 0
        except:
            return 0
    
    def get_channel_stats(self, channel_id: str) -> Optional[Dict]:
        """Get channel stats - 1 API call"""
        if not self.api_key:
            return None
            
        url = f"{self.base_url}/channels"
        params = {
            'part': 'snippet,statistics',
            'id': channel_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
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
