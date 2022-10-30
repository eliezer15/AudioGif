from db_models import Video, User, Favorite
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telegram import Video as TelegramVideo, User as TelegramUser
from typing import  List
from video_search import VideoSearch
from string import punctuation
class VideoRepository:
    
    MAX_VIDEOS_SEARCH_RESULT = 50

    def __init__(self, db_filename: str, search_filename: str):
        engine = create_engine(f'sqlite:///{db_filename}', echo=True)
        Session = sessionmaker(bind=engine)
        self.session = Session()

        self.video_search = VideoSearch(search_filename)

    def search_videos(self, query: str, telegram_user: TelegramUser) -> List[Video]:
        if len(query) == 0:
            return self.__get_default_videos_for_user(telegram_user)
        else:
            return self.__get_videos_by_search_query(query)

    def save_video(self, caption: str, telegram_video: TelegramVideo, telegram_user: TelegramUser) -> str:
        if caption == '':
            return 'El video no incluye ningun caption, no sera guardado.'

        elif len(caption) > 32:
            return 'El caption tiene mas de 32 caracteres. Sube el video con un caption mas corto.'

        self.__save_user_if_not_exist(telegram_user)

        video_model = Video(
            video_id = telegram_video.file_unique_id,
            playable_video_id = telegram_video.file_id,
            title = caption
        )
        self.session.add(video_model)
        self.session.commit()

        self.__add_video_to_search_index(video_model)

        return 'Video guardado exitosamente.'

    def save_favorite(self, telegram_video: TelegramVideo, telegram_user: TelegramUser) -> str:
        existing_video = self.session.query(Video).get(telegram_video.file_unique_id)
        if existing_video is None:
            return 'Este video no es parte de AudioGif.'
        
        self.__save_user_if_not_exist(telegram_user)

        existing_favorites = self.session.query(Favorite).filter_by(user_id=telegram_user.id).count()

        if existing_favorites > 49:
            return 'Solo se permite un maximo de 50 favoritos.'

        favorite_model = Favorite(user_id=telegram_user.id, video_id=telegram_video.file_unique_id)
        self.session.add(favorite_model)
        self.session.commit()

        return 'Favorito guardado exitosamente.'

    def save_search_terms(self, telegram_video: TelegramVideo, search_terms: List[str]) -> str:
        existing_video = self.session.query(Video).get(telegram_video.file_unique_id)
        if existing_video is None:
            return 'Este video no es parte de AudioGif.'
        
        self.video_search.add_search_terms(telegram_video.file_unique_id, search_terms)
        return 'Terminos de busqueda guardados exitosamente.'

    def get_all_videos(self) -> List[Video]:
        return self.session.query(Video).all()

    def __save_user_if_not_exist(self, user: TelegramUser):
        if self.session.query(User).get(user.id) is None:
            print(f'User {user.username} not found, saving to DB.')
            user_model = User(user_id=user.id, username=user.username)
            self.session.add(user_model)
            self.session.commit()

    def __get_default_videos_for_user(self, user: TelegramUser):
        results = []

        favorites = self.session.query(Video).join(Favorite).filter_by(user_id=user.id).all()
        for video in favorites:
            video.title = f'⭐ {video.title}'
            results.append(video)

        videos_left = self.MAX_VIDEOS_SEARCH_RESULT - len(results)
        other_videos = self.session.query(Video).limit(videos_left).all()

        results.extend(other_videos)
        return results
    
    def __get_videos_by_search_query(self, query: str):
        video_ids = self.video_search.find_video_ids(query)

        ''' 
        TODO: figure out how to make the "in" operator work to query the videos directly. For now, just getting all one by one
        videos = self.session.query(Video).filter(Video.video_id.in_(video_ids)).all()
        '''
        
        result = []
        for id in video_ids:
            result.append(self.session.query(Video).get(id))
        
        return result
    
    def __add_video_to_search_index(self, video: Video):
        search_terms = self.__get_search_terms_from_title(video.title)
        self.video_search.add_search_terms(video.video_id, search_terms)

    def __get_search_terms_from_title(self, title: str) -> List[str]:
        #1 Strip punctuation from it
        table = str.maketrans(dict.fromkeys(punctuation))
        stripped_title = title.translate(table)

        #2 Split by space
        terms = stripped_title.split() #Split with no arguments splits by whitespace

        #3 Remove one letter words
        filtered_terms = filter(lambda term: len(term) > 1, terms)

        # Finally, remove duplicates
        return list(set(filtered_terms))