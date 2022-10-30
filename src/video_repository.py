from db_models import Video, User, Favorite
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telegram import Video as TelegramVideo, User as TelegramUser
from typing import  List


class VideoRepository:
    
    MAX_VIDEOS_SEARCH_RESULT = 50

    def __init__(self, db_filename: str):
        engine = create_engine(f'sqlite:///{db_filename}', echo=True)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def save_video(self, caption: str, telegram_video: TelegramVideo, telegram_user: TelegramUser):
        if caption == '':
            return 'El video no incluye ningun caption, no sera guardado.'

        elif len(caption) > 32:
            return 'El caption tiene mas de 32 caracteres. Sube el video con un caption mas corto.'

        self.save_user_if_not_exist(telegram_user)

        video_model = Video(
            video_id = telegram_video.file_unique_id,
            playable_video_id = telegram_video.file_id,
            title = caption
        )
        self.session.add(video_model)
        self.session.commit()

        return 'Video guardado exitosamente.'

    def save_user_if_not_exist(self, user: TelegramUser):
        if self.session.query(User).get(user.id) is None:
            print(f'User {user.username} not found, saving to DB.')
            user_model = User(user_id=user.id, username=user.username)
            self.session.add(user_model)
            self.session.commit()

    def favorite(self, telegram_video: TelegramVideo, telegram_user: TelegramUser) -> str:
        existing_video = self.session.query(Video).get(telegram_video.file_unique_id)
        if existing_video is None:
            return 'Este video no es parte de AudioGif.'
        
        self.save_user_if_not_exist(telegram_user)

        existing_favorites = self.session.query(Favorite).filter_by(user_id=telegram_user.id).count()

        if existing_favorites > 49:
            return 'Solo se permite un maximo de 50 favoritos.'

        favorite_model = Favorite(user_id=telegram_user.id, video_id=telegram_video.file_unique_id)
        self.session.add(favorite_model)
        self.session.commit()

        return 'Favorito guardado exitosamente.'