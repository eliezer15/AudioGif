from database import db_models as db
from telegram import Video as TelegramVideo, User as TelegramUser

"""
These classes are the core business entities and represent the bridge between
Telegram API models and DB models.
"""

class Video:
    def __init__(self, video_id: str = '',
        playable_video_id: str = '',
        title: str = '',
        uploaded_by: str = ''
    ):
        self.video_id = video_id
        self.playable_video_id = playable_video_id
        self.title = title
        self.uploaded_by = uploaded_by

    def to_db_model(self) -> db.Video:
        db_video = db.Video()
        db_video.video_id = self.video_id
        db_video.playable_video_id = self.playable_video_id
        db_video.title = self.title
        db_video.uploaded_by = self.uploaded_by
        return db_video
    
    def from_db_model(db_video: db.Video):
        video = Video()
        video.video_id = db_video.video_id
        video.playable_video_id = db_video.playable_video_id
        video.title = db_video.title
        video.uploaded_by = db_video.uploaded_by
        return video
    
    def from_telegram_video(telegram_video: TelegramVideo, caption: str):
        video = Video()
        video.video_id = telegram_video.file_id
        video.playable_video_id = telegram_video.file_unique_id
        video.title = caption
        return video
    
    def __str__(self):
        return f'Video: {self.title}; {self.video_id}; {self.playable_video_id}; {self.uploaded_by}'

class Favorite:
    def __init__(self, user_id: str, video_id: str):
        self.user_id = user_id
        self.video_id = video_id
    
    def to_db_model(self) -> db.Favorite:
        db_favorite = db.Favorite()
        db_favorite.user_id = self.user_id
        db_favorite.video_id = self.video_id
        return db_favorite

    def from_db_model(db_favorite: db.Favorite):
        favorite = Favorite(db_favorite.user_id, db_favorite.video_id)
        return favorite
    
    def __str__(self):
        return f'Favorite: {self.user_id}; {self.video_id}'


class User:
    def __init__(self, user_id: str = '', username: str = ''):
        self.user_id = user_id
        self.username = username
    
    def from_db_model(db_user: db.User):
        user = User()
        user.user_id = db_user.user_id
        user.username = db_user.username
        return user
    
    def to_db_model(self) -> db.User:     
        db_user = db.User()
        db_user.user_id = self.user_id
        db_user.username = self.username
        return db_user

    def from_telegram_user(telegram_user: TelegramUser):
        user = User()
        user.user_id = telegram_user.id
        user.username = telegram_user.username
        return user
    
    def __str__(self) -> str:
        return f'User: {self.user_id}; {self.username}'
    