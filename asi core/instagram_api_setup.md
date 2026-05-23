# Instagram API Setup Guide

## Prerequisites
1. Meta Developer Account
2. Instagram Business or Creator Account
3. Facebook Page (for Business/Creator accounts)

## Getting Your Access Token

### Method 1: Instagram Basic Display API (Personal Accounts)
1. Go to [Meta Developers](https://developers.facebook.com/)
2. Create a new app or use existing one
3. Add "Instagram Basic Display" product
4. Configure Instagram Basic Display:
   - Add your Instagram Test Users
   - Set valid OAuth redirect URIs
5. Generate access token via OAuth flow

### Method 2: Instagram Graph API (Business/Creator Accounts)
1. Go to [Meta Developers](https://developers.facebook.com/)
2. Create Business app
3. Add "Instagram Graph API" product
4. Get permissions: `instagram_basic`, `pages_show_list`, `instagram_manage_insights`
5. Generate long-lived access token

## Quick Test Script

```python
from instagram_api_fetch import InstagramAPI

# Replace with your access token
ACCESS_TOKEN = "YOUR_ACTUAL_ACCESS_TOKEN"

api = InstagramAPI(ACCESS_TOKEN)

# Test basic functionality
profile = api.get_user_profile()
print("Profile:", profile)

media = api.get_user_media(limit=5)
print("Recent media:", media)
```

## Common Endpoints

- **User Profile**: `/{user-id}?fields=id,username,account_type,media_count,followers_count`
- **User Media**: `/{user-id}/media?fields=id,caption,media_type,media_url,permalink,timestamp`
- **Media Details**: `/{media-id}?fields=id,caption,media_type,media_url,permalink,timestamp,like_count`
- **Media Comments**: `/{media-id}/comments?fields=id,text,timestamp,username`

## Rate Limits
- 200 calls per hour per user
- 1000 calls per hour per app
- Use pagination for large datasets

## Error Handling
Common errors and solutions:
- `190`: Invalid access token - regenerate token
- `200`: Permissions missing - update app permissions
- `4`: Application limit reached - wait and retry
