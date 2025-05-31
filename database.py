from pymongo import MongoClient
from typing import Optional, List, Dict

class MongoDB:
    def __init__(self, uri: str):
        self.client = MongoClient(uri)
        self.db = self.client["drm_uploader"]
        self.users = self.db["users"]
        self.activities = self.db["activities"]
    
    def is_user_authorized(self, user_id: int) -> bool:
        """Check if user is authorized to use the bot"""
        user = self.users.find_one({"user_id": user_id})
        return user is not None
    
    def log_activity(self, user_id: int, platform: str, content_title: str):
        """Log user activity"""
        self.activities.insert_one({
            "user_id": user_id,
            "platform": platform,
            "content_title": content_title,
            "timestamp": datetime.utcnow()
        })
    
    def get_user_activities(self, user_id: int) -> List[Dict]:
        """Get all activities for a user"""
        return list(self.activities.find({"user_id": user_id}).sort("timestamp", -1))
    
    def add_user(self, user_id: int, username: Optional[str] = None):
        """Add a new authorized user"""
        if not self.is_user_authorized(user_id):
            self.users.insert_one({
                "user_id": user_id,
                "username": username,
                "added_at": datetime.utcnow()
            })
    
    def remove_user(self, user_id: int):
        """Remove user authorization"""
        self.users.delete_one({"user_id": user_id})
