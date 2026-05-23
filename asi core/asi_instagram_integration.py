#!/usr/bin/env python3
"""
ASI-Instagram Integration Bridge
Connects ASI authentication system with Instagram API endpoints
"""

import requests
import json
import sys
import os
from typing import Dict, Any, Optional

# Add ASI- engine to path for integration
sys.path.append(os.path.join(os.path.dirname(__file__), 'ASI-'))

from engine.auth.auth import AuthManager
from engine.api.server import APIServer
from engine.core.graph import NodeGraph

class ASIInstagramBridge:
    """
    Bridge between ASI system and Instagram API.
    Manages credentials and provides unified interface.
    """
    
    def __init__(self, asi_port: int = 8000):
        """
        Initialize ASI-Instagram bridge.
        
        Args:
            asi_port: Port where ASI API server is running
        """
        self.asi_port = asi_port
        self.asi_base_url = f"http://localhost:{asi_port}"
        self.auth = AuthManager()
        self.graph = NodeGraph()
        
        # Create Instagram admin user in ASI
        self.instagram_admin = self.auth.create_user("instagram_admin", "admin")
        print(f"ASI Instagram admin token: {self.instagram_admin.token}")
        
    def get_asi_token(self) -> str:
        """Get ASI authentication token for Instagram operations."""
        return self.instagram_admin.token
    
    def start_asi_server(self, nodes: int = 10):
        """Start ASI API server for credential management."""
        print(f"Starting ASI server on port {self.asi_port}...")
        
        # Bootstrap nodes
        self.graph.bootstrap(nodes)
        print(f"Bootstrapped {nodes} ASI nodes")
        
        # Start server (in background)
        server = APIServer(
            graph=self.graph, 
            auth=self.auth, 
            ingester=None,
            host="0.0.0.0", 
            port=self.asi_port
        )
        
        print(f"ASI API server running at {self.asi_base_url}")
        print("Available endpoints:")
        print("  POST /auth/token   - Get Bearer token")
        print("  POST /query        - Query ASI graph")
        print("  GET  /stats        - System statistics")
        
        return server
    
    def create_instagram_client(self, instagram_token: str = None):
        """Create Instagram API client using ASI credentials."""
        from instagram_api_fetch import InstagramAPI
        
        # Use ASI token if no Instagram token provided
        if not instagram_token:
            instagram_token = self.get_asi_token()
        
        return InstagramAPI(access_token=instagram_token, asi_auth=self.auth)
    
    def setup_instagram_feed_in_asi(self):
        """Add Instagram as a data source to ASI system."""
        # This would integrate Instagram data into ASI's semantic map
        print("Setting up Instagram feed integration in ASI...")
        
        # Example: Add Instagram endpoint to ASI's feed system
        instagram_config = {
            "source": "instagram",
            "endpoint": "https://graph.instagram.com/me/media",
            "auth_method": "bearer_token",
            "token": self.get_asi_token(),
            "update_interval": 300  # 5 minutes
        }
        
        # Store configuration in ASI graph
        self.graph.index_text(
            f"Instagram feed configuration: {json.dumps(instagram_config)}",
            tags=["instagram", "feed", "social_media"]
        )
        
        print("Instagram feed configured in ASI semantic map")

def main():
    """Main function to demonstrate ASI-Instagram integration."""
    print("=== ASI-Instagram Integration Bridge ===\n")
    
    # Initialize bridge
    bridge = ASIInstagramBridge()
    
    # Create Instagram client using ASI credentials
    print("Creating Instagram API client with ASI credentials...")
    instagram_client = bridge.create_instagram_client()
    
    # Setup Instagram feed in ASI
    bridge.setup_instagram_feed_in_asi()
    
    # Test Instagram API (will use ASI token)
    print("\nTesting Instagram API with ASI credentials...")
    try:
        profile = instagram_client.get_user_profile()
        print("Instagram profile response:")
        print(json.dumps(profile, indent=2))
    except Exception as e:
        print(f"Instagram API test failed: {e}")
        print("Note: You need a valid Instagram access token for actual API calls")
    
    print(f"\nASI Instagram admin token: {bridge.get_asi_token()}")
    print("Use this token for Instagram API authentication")
    print("ASI API server available at: http://localhost:8000")

if __name__ == "__main__":
    main()
