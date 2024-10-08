from typing import List
from database.db_models import Video, User, Favorite
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from service.utils import remove_accents_and_punctuation

class Repository:
    """
    Abstracts all database operations.
    """

    def __init__(self, db_path: str):
        """
        Creates a new repository object.

        :param db_path: path to the database file
        """
        engine = create_engine(f'{db_path}', echo=True)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def insert_video(self, video: Video):
        """
        Inserts a video into the database.

        :param video: the video to insert
        """
        self.session.add(video)
        self.session.commit()
    
    def delete_video_by_id(self, video_id: str):
        """
        Deletes a video from the database by its id.

        :param video_id: the video id
        """
        self.session.query(Video).filter(Video.video_id == video_id).delete()
        self.session.commit()

    def insert_favorite(self, favorite: Favorite):
        """
        Inserts a favorite into the database.

        :param favorite: the favorite to insert
        """
        self.session.add(favorite)
        self.session.commit()
    
    def delete_favorite(self, favorite: Favorite):
        """
        Deletes a favorite from the database

        :param favorite: the favorite to delete
        """

        self.session.query(Favorite).filter(Favorite.video_id == favorite.video_id, Favorite.user_id == favorite.user_id).delete()
        self.session.commit()

    def insert_user_if_not_exist(self, user: User):
        """
        Inserts a user into the database if it does not exist.

        :param user: the user to insert
        """
        existing_user = self.session.query(User).get(user.user_id)
        if existing_user is None:
            self.session.add(user)
            self.session.commit()

    def get_all_videos(self, limit: int, title_start_with: str = None) -> List[Video]:
        """
        Gets all videos from the database.

        :return: all videos
        """
        query = self.session.query(Video)
        if title_start_with is not None:
            query = query.filter(Video.title.startswith(title_start_with))
        
        return query.order_by(Video.title).limit(limit).all()

    def get_videos_by_ids(self, video_ids: List[str], limit: int) -> List[Video]:
        """
        Gets all videos from the database by their ids.

        :param video_ids: the video ids
        :return: all videos
        """
        return self.session.query(Video).filter(Video.video_id.in_(video_ids)).limit(limit).all()

    def get_videos_by_user(self, user: User) -> List[Video]:
        """
        Gets all videos from the database by user who uploaded them.

        :param user: the user 
        :return: all videos
        """

        return self.session.query(Video).filter(Video.uploaded_by == user.user_id).all()

    def get_videos_like_title(self, title: str, limit: int = 100) -> List[Video]:
        """
        Gets all videos from the database that have a title like the given title.

        :param title: the title
        :return: all videos
        """
        search_title = remove_accents_and_punctuation(title)
        return self.session.query(Video).filter(Video.search_title.like(f'%{search_title}%')).limit(limit).all()
    
    def get_video_by_id(self, video_id: str) -> Video:
        """
        Gets a video from the database by its id.

        :param video_id: the video id
        :return: the video
        """
        return self.session.query(Video).get(video_id)

    def get_favorite_videos(self, user_id: str) -> List[Video]:
        """
        Gets all favorite videos from the database for a specific user.

        :param user_id: the user id
        :return: all favorite videos
        """
        return self.session.query(Video).join(Favorite).filter(Favorite.user_id == user_id).all()

    def get_favorite_videos_count(self, user_id: str) -> int:
        """
        Gets the number of favorite videos for a specific user.

        :param user_id: the user id
        :return: the number of favorite videos
        """
        return self.session.query(Favorite).filter(Favorite.user_id == user_id).count()
    
    def update_video_title(self, video_id: str, new_title: str):
        self.session.query(Video)\
            .filter(Video.video_id == video_id)\
            .update({'title': new_title, 'search_title': remove_accents_and_punctuation(new_title)})
        
        self.session.commit()


    