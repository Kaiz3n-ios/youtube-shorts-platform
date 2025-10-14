import requests
import os
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class YouTubeService:
    def __init__(self):
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        
        # Multi-niche search strategy
        self.NICHE_KEYWORDS = {
            'gaming': ['gaming shorts', 'game clips', 'game highlights', 'gaming moments'],
            'finance': ['money tips', 'investing shorts', 'finance hacks', 'wealth building'],
            'comedy': ['funny shorts', 'comedy sketches', 'humor videos', 'laugh clips'],
            'education': ['learn quick', 'knowledge shorts', 'educational', 'facts daily'],
            'lifestyle': ['life hacks', 'daily tips', 'lifestyle tips', 'self improvement'],
            'tech': ['tech shorts', 'ai news', 'gadget reviews', 'coding tips'],
            'fitness': ['workout shorts', 'fitness tips', 'health hacks', 'exercise'],
            'cooking': ['recipe shorts', 'cooking tips', 'food hacks', 'quick meals']
        }
        
        # Spam/quality detection
        self.SPAM_KEYWORDS = [
            'sub4sub', 'like4like', 'get rich quick', 'instant money',
            'free subscribers', 'viral trick', 'algorithm hack'
        ]
        
        if not self.api_key:
            print("❌ YOUTUBE_API_KEY not found!")
        else:
            print("✅ YouTube API Key loaded successfully")
    
    def discover_emerging_channels(self, max_results: int = 20) -> List[Dict]:
        """Enhanced discovery across multiple niches"""
        if not self.api_key:
            return [{"error": "API Key missing"}]
        
        print("🔍 Multi-niche hunting for emerging viral channels...")
        
        all_potential_channels = []
        
        # Search across all niches
        for niche, keywords in self.NICHE_KEYWORDS.items():
            print(f"🎯 Searching {niche} niche...")
            
            for keyword in keywords[:2]:  # Use first 2 keywords per niche
                try:
                    channels = self._search_emerging_in_niche(keyword, niche, max_per_keyword=5)
                    all_potential_channels.extend(channels)
                    time.sleep(0.3)  # Rate limiting
                except Exception as e:
                    print(f"❌ Error searching {keyword}: {e}")
                    continue
        
        # Remove duplicates and apply quality filters
        unique_channels = self._remove_duplicates(all_potential_channels)
        quality_channels = [c for c in unique_channels if self._is_quality_channel(c)]
        
        # Score and sort by potential
        scored_channels = [self._calculate_channel_potential(c) for c in quality_channels]
        scored_channels.sort(key=lambda x: x.get('potential_score', 0), reverse=True)
        
        # Return top results
        emerging_channels = [c for c in scored_channels if c.get('is_emerging', False)]
        
        print(f"✅ Found {len(emerging_channels)} emerging channels across {len(self.NICHE_KEYWORDS)} niches")
        return emerging_channels[:max_results]
    
    def _search_emerging_in_niche(self, keyword: str, niche: str, max_per_keyword: int = 5) -> List[Dict]:
        """Search for emerging channels in specific niche"""
        url = f"{self.base_url}/search"
        params = {
            'part': 'snippet',
            'q': f'{keyword} #shorts',
            'type': 'video',
            'maxResults': 15,
            'order': 'date',  # Get newest content
            'publishedAfter': (datetime.utcnow() - timedelta(days=60)).isoformat() + 'Z',
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            channels_found = []
            
            for item in data.get('items', []):
                channel_id = item['snippet']['channelId']
                
                # Skip if we already have this channel
                if any(c.get('channel_id') == channel_id for c in channels_found):
                    continue
                
                # Analyze channel potential
                channel_analysis = self._analyze_channel_potential(channel_id, niche)
                
                if channel_analysis and channel_analysis.get('is_potential_emerging'):
                    channels_found.append(channel_analysis)
                
                if len(channels_found) >= max_per_keyword:
                    break
                    
            return channels_found
            
        except Exception as e:
            print(f"❌ Niche search error for {keyword}: {e}")
            return []
    
    def _analyze_channel_potential(self, channel_id: str, niche: str) -> Optional[Dict]:
        """Enhanced channel analysis with niche context"""
        try:
            # Get channel stats
            channel_stats = self.get_channel_stats(channel_id)
            if not channel_stats:
                return None
            
            # Get recent videos for viral analysis
            recent_videos = self._get_channel_recent_videos(channel_id, max_results=12)
            
            # Calculate enhanced metrics
            analysis = self._calculate_enhanced_metrics(channel_stats, recent_videos, niche)
            
            return analysis
            
        except Exception as e:
            print(f"❌ Channel analysis error: {e}")
            return None
    
    def _calculate_enhanced_metrics(self, channel_stats: Dict, recent_videos: List[Dict], niche: str) -> Dict:
        """Calculate enhanced metrics for channel potential"""
        # Sort videos by publish date (newest first)
        recent_videos.sort(key=lambda x: x['published_at'], reverse=True)
        
        # Take last 10-12 videos for analysis
        analyzed_videos = recent_videos[:12] if len(recent_videos) >= 10 else recent_videos
        
        # Viral video analysis
        viral_count = sum(1 for video in analyzed_videos if video['view_count'] >= 1000000)
        million_plus_views = [v for v in analyzed_videos if v['view_count'] >= 1000000]
        
        # Engagement analysis
        total_engagement = sum(v.get('like_count', 0) for v in analyzed_videos)
        avg_engagement = total_engagement / len(analyzed_videos) if analyzed_videos else 0
        
        # Growth velocity (simplified)
        if len(analyzed_videos) >= 5:
            recent_avg_views = sum(v['view_count'] for v in analyzed_videos[:5]) / 5
            older_avg_views = sum(v['view_count'] for v in analyzed_videos[5:10]) / 5 if len(analyzed_videos) >= 10 else recent_avg_views
            growth_velocity = (recent_avg_views - older_avg_views) / (older_avg_views + 1)
        else:
            growth_velocity = 0
        
        # Channel age estimate
        channel_age = self._estimate_channel_age(analyzed_videos)
        
        analysis = {
            **channel_stats,
            'niche': niche,
            'viral_video_count': viral_count,
            'total_viral_views': sum(v['view_count'] for v in million_plus_views),
            'avg_recent_views': sum(v['view_count'] for v in analyzed_videos) / len(analyzed_videos) if analyzed_videos else 0,
            'recent_videos_analyzed': len(analyzed_videos),
            'channel_age_days': channel_age,
            'engagement_per_video': avg_engagement,
            'growth_velocity': growth_velocity,
            'is_potential_emerging': viral_count >= 2 and channel_age <= 120,  # 2 viral videos in 4 months
            'quality_score': self._calculate_quality_score(channel_stats, analyzed_videos)
        }
        
        return analysis
    
    def _calculate_quality_score(self, channel_stats: Dict, videos: List[Dict]) -> float:
        """Calculate channel quality score (0-10)"""
        score = 5.0  # Base score
        
        # Subscriber quality (not too big, not too small)
        subs = channel_stats['subscriber_count']
        if 5000 <= subs <= 200000:
            score += 2.0
        elif subs > 1000000:
            score -= 1.0  # Penalize very large channels
        
        # View-to-sub ratio
        view_sub_ratio = channel_stats['view_count'] / (subs + 1)
        if 2.0 <= view_sub_ratio <= 50.0:
            score += 1.5
        elif view_sub_ratio > 100.0:
            score -= 1.0
        
        # Content consistency
        if len(videos) >= 8:
            score += 1.0
        
        # Spam detection
        description = channel_stats.get('description', '').lower()
        if any(spam in description for spam in self.SPAM_KEYWORDS):
            score -= 3.0
        
        return max(0.0, min(10.0, score))
    
    def _calculate_channel_potential(self, channel_data: Dict) -> Dict:
        """Calculate overall potential score"""
        base_score = 0.0
        
        # Viral potential (40%)
        viral_score = min(4.0, channel_data['viral_video_count'] * 1.0)
        base_score += viral_score
        
        # Growth velocity (30%)
        velocity_score = min(3.0, max(0.0, channel_data['growth_velocity'] * 10))
        base_score += velocity_score
        
        # Quality score (20%)
        quality_score = channel_data.get('quality_score', 5.0) * 0.2
        base_score += quality_score
        
        # Engagement (10%)
        engagement_score = min(1.0, channel_data.get('engagement_per_video', 0) / 10000)
        base_score += engagement_score
        
        channel_data['potential_score'] = round(base_score, 2)
        channel_data['is_emerging'] = (
            channel_data['is_potential_emerging'] and 
            channel_data['potential_score'] >= 3.0 and
            channel_data['subscriber_count'] <= 300000
        )
        
        return channel_data
    
    def _is_quality_channel(self, channel_data: Dict) -> bool:
        """Enhanced quality filtering"""
        return (
            channel_data.get('quality_score', 0) >= 3.0 and
            not any(spam in channel_data.get('description', '').lower() for spam in self.SPAM_KEYWORDS) and
            channel_data.get('subscriber_count', 0) >= 1000 and
            channel_data.get('subscriber_count', 0) <= 1000000
        )
    
    def _remove_duplicates(self, channels: List[Dict]) -> List[Dict]:
        """Remove duplicate channels"""
        seen = set()
        unique = []
        for channel in channels:
            channel_id = channel.get('channel_id')
            if channel_id and channel_id not in seen:
                seen.add(channel_id)
                unique.append(channel)
        return unique
    
    # Keep existing helper methods from previous version:
    def _estimate_channel_age(self, videos: List[Dict]) -> int:
        """Estimate channel age in days based on video publish dates"""
        if not videos:
            return 365
        publish_dates = [datetime.fromisoformat(v['published_at'].replace('Z', '')) for v in videos]
        oldest_video = min(publish_dates)
        days_old = (datetime.utcnow() - oldest_video).days
        return min(days_old, 365)
    
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
                'description': channel['snippet']['description'],
                'subscriber_count': int(stats.get('subscriberCount', 0)),
                'view_count': int(stats.get('viewCount', 0)),
                'video_count': int(stats.get('videoCount', 0)),
                'published_at': channel['snippet']['publishedAt'],
            }
            
            return channel_data
            
        except Exception as e:
            print(f"❌ Channel stats error: {e}")
            return None
