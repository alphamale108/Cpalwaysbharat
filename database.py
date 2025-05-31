from datetime import datetime  # यह लाइन जरूर जोड़ें
from pymongo import MongoClient
from config import Config

class Database:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client.course_extractor_bot
    
    def add_user(self, user_id, username, first_name, last_name):
        users = self.db.users
        user_data = {
            'user_id': user_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'joined_at': datetime.now()
        }
        users.update_one({'user_id': user_id}, {'$set': user_data}, upsert=True)
    
    def log_request(self, user_id, platform, course_name):
        requests = self.db.requests
        request_data = {
            'user_id': user_id,
            'platform': platform,
            'course_name': course_name,
            'requested_at': datetime.now()
        }
        requests.insert_one(request_data)
    
    def get_user_stats(self, user_id):
        requests = self.db.requests
        return requests.count_documents({'user_id': user_id})
