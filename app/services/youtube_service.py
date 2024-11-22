from googleapiclient.discovery import build
from app.models.nutrition_models import VideoInfo
import logging
from typing import Optional, List

class YouTubeService:
    """
    Service class for interacting with YouTube Data API
    Handles fetching recipe videos for food items
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)

    def get_recipe_videos(self, is_recipe: bool, food_item: str, max_results: int = 10) -> Optional[List[VideoInfo]]:
        """
        Fetches recipe videos for a given food item from YouTube
        Args:
            food_item: Name of the food/recipe to search for
            max_results: Maximum number of videos to return
        Returns:
            List of VideoInfo objects or None if no videos found/error occurs
        """
        if not self.api_key:
            self.logger.error("YouTube API key not found")
            return None

        try:
            youtube = build('youtube', 'v3', 
                          developerKey=self.api_key)
            search_response = None
            if is_recipe:
                search_response = youtube.search().list(
                    q=f"how to make {food_item} recipe",
                    part='id,snippet',
                    maxResults=max_results,
                    type='video',
                    regionCode='IN'
                ).execute()
            else:
                search_response = youtube.search().list(
                    q=f"suggest me a few recipes with {food_item}",
                    part='id,snippet',
                    maxResults=max_results,
                    type='video',
                    regionCode='IN'
                ).execute()

            if not search_response.get('items'):
                self.logger.warning(f"No videos found for {food_item}")
                return None

            videos = [
                VideoInfo(
                    url=f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                    id=item['id']['videoId'],
                    title=item['snippet']['title']
                )
                for item in search_response['items']
            ]
            
            return videos

        except Exception as e:
            self.logger.error(f"YouTube API error: {str(e)}")
            return None 