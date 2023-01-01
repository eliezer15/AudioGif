from typing import List
from database.repository import Repository
from service.domain_models import Video, User, Favorite

class VideoService:

    MAX_VIDEOS_RESULT = 600

    def __init__(self, repository: Repository):
        self.repository = repository
    
    def search_videos(self, query: str, user: User) -> List[Video]:
        query_length = len(query)
        if query_length == 0:
            return self.__get_default_videos_for_user(user)
        elif query_length == 1:
            return self.__get_all_videos_starting_with(query)
        else:
            return self.__get_videos_by_search_query(query)

    def save_video(self, caption: str, video: Video, user: User) -> str:
        video.uploaded_by = user.user_id

        if caption == '':
            return 'El video no incluye ningun caption, no sera guardado.'

        elif len(caption) > 32:
            return 'El caption tiene mas de 32 caracteres. Sube el video con un caption mas corto.'

        self.repository.insert_user_if_not_exist(user.to_db_model())
        self.repository.insert_video(video.to_db_model())

        return 'Video guardado exitosamente.'
    
    def save_favorite(self, video: Video, user: User) -> str:
        existing_video = self.repository.get_video_by_id(video.video_id)
        if existing_video is None:
            return 'Este video no es parte de AudioGif.'
        
        self.repository.insert_user_if_not_exist(user.to_db_model())

        existing_favorites = self.repository.get_favorite_videos_count(user.user_id)
        if existing_favorites >= self.MAX_VIDEOS_RESULT:
            return f'Solo se permite un maximo de {self.MAX_VIDEOS_RESULT} favoritos.'

        favorite_model = Favorite(user_id=user.user_id, video_id=video.video_id).to_db_model()
        self.repository.insert_favorite(favorite_model)

        return 'Favorito guardado exitosamente.'
    
    def delete_video(self, video: Video) -> str:
        existing_video = self.repository.get_video_by_id(video.video_id)
        if existing_video is None:
            return 'Este video no es parte de AudioGif.'
        
        self.repository.delete_video_by_id(video.video_id)
        return 'Video borrado exitosamente.'
    
    def __get_default_videos_for_user(self, user: User) -> List[Video]:
        results = []
        favorites = self.repository.get_favorite_videos(user.user_id)
        for db_video in favorites:
            video = Video.from_db_model(db_video)
            video.title = f'⭐ {video.title}'
            results.append(video)
        
        videos_left = self.MAX_VIDEOS_RESULT - len(results)
        default_videos = self.repository.get_all_videos(videos_left)

        results.extend(default_videos)
        return results
    
    def __get_videos_by_search_query(self, query: str) -> List[Video]:
        db_videos = self.repository.get_videos_like_title(query)
        #db_videos = self.repository.get_videos_by_ids(video_ids, 100)
        return [Video.from_db_model(db_video) for db_video in db_videos]

    def __get_all_videos_starting_with(self, query: str) -> List[Video]:
        db_videos = self.repository.get_all_videos(self.MAX_VIDEOS_RESULT, query)
        return [Video.from_db_model(db_video) for db_video in db_videos]