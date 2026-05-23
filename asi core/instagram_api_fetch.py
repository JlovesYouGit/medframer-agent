import requests
import json
import sys
import os
from typing import Dict, Any, Optional

# Add ASI- engine to path for integration
sys.path.append(os.path.join(os.path.dirname(__file__), 'ASI-'))

from engine.auth.auth import AuthManager

class InstagramAPI:
    def __init__(self, access_token: str = None, asi_auth: AuthManager = None):
        """
        Initialize Instagram API client with access token or ASI integration.
        
        Args:
            access_token: Your Instagram Graph API access token (optional if using ASI)
            asi_auth: ASI AuthManager instance for credential management (optional)
        """
        self.base_url = "https://graph.instagram.com"
        
        # Use ASI auth if available, otherwise use provided token
        if asi_auth:
            self.asi_auth = asi_auth
            # Get admin user from ASI for Instagram operations
            admin_users = [u for u in asi_auth.list_users() if u['role'] == 'admin']
            if admin_users:
                self.access_token = self._get_instagram_token_from_asi(admin_users[0]['username'])
            else:
                # Create admin user if none exists
                admin = asi_auth.create_user("instagram_admin", "admin")
                self.access_token = self._get_instagram_token_from_asi(admin.username)
        else:
            self.access_token = access_token
            self.asi_auth = None
    
    def _get_instagram_token_from_asi(self, username: str) -> str:
        """
        Generate Instagram-compatible token from ASI user credentials.
        This creates a bridge between ASI authentication and Instagram API.
        """
        if not self.asi_auth:
            return "YOUR_ACCESS_TOKEN_HERE"
        
        user = self.asi_auth._users.get(username)
        if user:
            # Use ASI token as Instagram token (in real implementation, you'd map this)
            return user.token
        return "YOUR_ACCESS_TOKEN_HERE"
        
    def get_user_profile(self, user_id: str = "me") -> Dict[str, Any]:
        """
        Get user profile information.
        
        Args:
            user_id: Instagram user ID (default: "me" for authenticated user)
            
        Returns:
            Dictionary containing user profile data
        """
        url = f"{self.base_url}/{user_id}"
        params = {
            "fields": "id,username,account_type,media_count,followers_count",
            "access_token": self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching user profile: {e}")
            return {"error": str(e)}
    
    def get_user_media(self, user_id: str = "me", limit: int = 25) -> Dict[str, Any]:
        """
        Get user's media posts.
        
        Args:
            user_id: Instagram user ID (default: "me" for authenticated user)
            limit: Number of media items to fetch (max 100)
            
        Returns:
            Dictionary containing media data
        """
        url = f"{self.base_url}/{user_id}/media"
        params = {
            "fields": "id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count",
            "limit": min(limit, 100),
            "access_token": self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching user media: {e}")
            return {"error": str(e)}
    
    def get_media_details(self, media_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific media item.
        
        Args:
            media_id: ID of the media item
            
        Returns:
            Dictionary containing media details
        """
        url = f"{self.base_url}/{media_id}"
        params = {
            "fields": "id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count,children",
            "access_token": self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching media details: {e}")
            return {"error": str(e)}
    
    def get_media_comments(self, media_id: str, limit: int = 25) -> Dict[str, Any]:
        """
        Get comments for a specific media item.
        
        Args:
            media_id: ID of the media item
            limit: Number of comments to fetch (max 100)
            
        Returns:
            Dictionary containing comments data
        """
        url = f"{self.base_url}/{media_id}/comments"
        params = {
            "fields": "id,text,timestamp,username,replies",
            "limit": min(limit, 100),
            "access_token": self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching media comments: {e}")
            return {"error": str(e)}

def main():
    """
    Example usage of Instagram API client with ASI integration.
    The system will automatically use ASI credentials for Instagram operations.
    """
    try:
        # Initialize ASI AuthManager
        asi_auth = AuthManager()
        
        # Initialize API client with ASI integration
        api = InstagramAPI(asi_auth=asi_auth)
        
        print("Instagram API initialized with ASI credentials")
        print(f"Using ASI base URI: http://localhost:8000 (ASI API server)")
        
        # Get user profile
        print("\nFetching user profile...")
        profile = api.get_user_profile()
        print(json.dumps(profile, indent=2))
        
        # Get user media
        print("\nFetching user media...")
        media = api.get_user_media(limit=10)
        print(json.dumps(media, indent=2))
        
        # If media exists, get details of first media item
        if "data" in media and media["data"]:
            first_media_id = media["data"][0]["id"]
            print(f"\nFetching details for media ID: {first_media_id}")
            media_details = api.get_media_details(first_media_id)
            print(json.dumps(media_details, indent=2))
            
            # Get comments for the first media item
            print(f"\nFetching comments for media ID: {first_media_id}")
            comments = api.get_media_comments(first_media_id, limit=5)
            print(json.dumps(comments, indent=2))
            
    except ImportError as e:
        print(f"ASI integration failed: {e}")
        print("Falling back to manual token configuration...")
        
        # Fallback to manual token
        ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"
        
        if ACCESS_TOKEN == "YOUR_ACCESS_TOKEN_HERE":
            print("Please replace 'YOUR_ACCESS_TOKEN_HERE' with your actual Instagram Graph API access token")
            print("Get your token from: https://developers.facebook.com/docs/instagram-basic-display-api/getting-started")
            return
        
        api = InstagramAPI(ACCESS_TOKEN)
        
        # Get user profile
        print("Fetching user profile...")
        profile = api.get_user_profile()
        print(json.dumps(profile, indent=2))
        
        # Get user media
        print("\nFetching user media...")
        media = api.get_user_media(limit=10)
        print(json.dumps(media, indent=2))

if __name__ == "__main__":
    main()
