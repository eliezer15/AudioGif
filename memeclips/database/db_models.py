from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Favorite(Base):
    __tablename__ = "favorites"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    video_id = Column(String, ForeignKey("videos.video_id"))

class Video(Base):
    __tablename__ = "videos"
    video_id = Column(String, primary_key=True)
    playable_video_id = Column(String)
    title = Column(String)
    uploaded_by = Column(String, ForeignKey("users.user_id"))

class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True)
    username = Column(String)


