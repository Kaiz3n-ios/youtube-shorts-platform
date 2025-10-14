import requests
import os
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class YouTubeService:
    def __init__(self):
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        
        # Simplified niche search
        self.NICHE_KEYWORDS = {
            'gaming': 'gaming shorts',
            'finance': 'money tips', 
            'comedy': 'funny shorts',
            'education': 'learn quick'
        }
        
        if not self.api_key:
            print("❌ YOUTUBE_API_KEY not found!")
        else:
            print("✅ YouTube API Key loaded")
    
    def discover_emerging_channels(self, max_results: int = 10) -> List[Dict]:
        """Fast discovery without timeout"""
        if not self.api_key:
            return [{"error": "API Key missing"}]
        
        print("🔍 Fast hunting for emerging channels...")
        
        channels_found = []
        
        # Search 2 niches instead of all
        niches_to_search = ['gaming', 'comedy']  # Fastest niches
        
        for niche in niches_to_search:
            try:
                keyword = self.NICHE_KEYWORDS[niche]
                print(f"🎯 Searching {niche}: {keyword}")
                
                # Fast search with fewer results
                channels = self._fast_search(keyword, niche, max_per_niche=3)
                channels_found.extend(channels)
                
            except Exception as e:
                print(f"❌ Error in {niche}: {e}")
                continue
        
        # Quick scoring
        scored_channels = [self._quick_score(c) for c in channels_found]
        scored_channels.sort(key=lambda x: x.get('potential_score', 0), reverse=True)
        
        emerging = [c for c in scored_channels if c.get('is_emerging', False)]
        
        print(f"✅ Found {len(emerging)} emerging channels")
        return emerging[:max_results]
    
    def _fast_search(self, keyword: str, niche: str, max_per_niche: int = 3) -> List[Dict]:
        """Fast search with minimal API calls"""
        url = f"{self.base_url}/search"
        params = {
            'part': 'snippet',
            'q': f'{keyword} #shorts',
            'type': 'video',
            'maxResults': 8,  # Fewer results
            'order': 'date',
            'publishedAfter': (datetime.utcnow() - timedelta(days=45)).isoformat() + 'Z',
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            channels = []
            for item in data.get('items', []):
                if len(channels) >= max_per_niche:
                    break
                    
                channel_id = item['snippet']['channelId']
                
                # Quick channel analysis
                channel_data = self._quick_analyze(channel_id, niche)
                if channel_data and channel_data.get('is_potential'):
                    channels.append(channel_data)
                
                time.sleep(0.1)  # Minimal delay
            
            return channels
            
        except Exception as e:
            print(f"❌ Fast search error: {e}")
            return []
    
    def _quick_analyze(self, channel_id: str, niche: str) -> Optional[Dict]:
        """Quick channel analysis without deep dive"""
        try:
            # Get basic channel stats
            channel_stats = self.get_channel_stats(channel_id)
            if not channel_stats:
                return None
            
            # Get only 5 recent videos for speed
            recent_videos = self._get_recent_videos_fast(channel_id, 5)
            
            # Quick viral check
            viral_count = sum(1 for v in recent_videos if v['view_count'] >= 500000)  # Lower threshold
            
            analysis = {
                **channel_stats,
                'niche': niche,
                'viral_video_count': viral_count,
                'recent_videos_analyzed': len(recent_videos),
                'avg_views': sum(v['view_count'] for v in recent_videos) / len(recent_videos) if recent_videos else 0,
                'is_potential': viral_count >= 1 and channel_stats['subscriber_count'] <= 300000
            }
            
            return analysis
            
        except Exception as e:
            print(f"❌ Quick analysis error: {e}")
            return None
    
    def _get_recent_videos_fast(self, channel_id: str, max_results: int = 5) -> List[Dict]:
        """Get recent videos quickly"""
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
                
                # Get basic video stats without detailed analysis
                view_count = self._get_view_count_fast(video_id)
                
                videos.append({
                    'video_id': video_id,
                    'view_count': view_count,
                    'published_at': item['snippet']['publishedAt']
                })
            
            return videos
            
        except Exception as e:
            print(f"❌ Fast videos error: {e}")
            return []
    
    def _get_view_count_fast(self, video_id: str) -> int:
        """Get view count quickly"""
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
    
    def _quick_score(self, channel_data: Dict) -> Dict:
        """Quick potential scoring"""
        score = 0.0
        
        # Viral potential
        score += min(3.0, channel_data['viral_video_count'] * 1.5)
        
        # Size bonus (smaller is better for emerging)
        subs = channel_data['subscriber_count']
        if subs <= 100000:
            score += 2.0
        elif subs <= 300000:
            score += 1.0
        
        # View consistency
        if channel_data['avg_views'] >= 100000:
            score += 1.0
        
        channel_data['potential_score'] = round(score, 2)
        channel_data['is_emerging'] = score >= 3.0
        
        return channel_data
    
    def get_channel_stats(self, channel_id: str) -> Optional[Dict]:
        """Get channel statistics (keep existing)"""
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
                'description': channel['snippet']['description'][:100] + '...' if channel['snippet']['description'] else '',
                'subscriber_count': int(stats.get('subscriberCount', 0)),
                'view_count': int(stats.get('viewCount', 0)),
                'video_count': int(stats.get('videoCount', 0)),
                'published_at': channel['snippet']['publishedAt'],
            }
            
        except Exception as e:
            print(f"❌ Channel stats error: {e}")
            return None
