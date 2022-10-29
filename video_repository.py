from fileinput import filename
from os import environ as env
from typing import Dict, List

class VideoRepository:
    
    MAX_VIDEOS_SEARCH_RESULT = 50

    def __init__(self, videos_filename: str, favorites_filename: str):
        self.videos_filename = videos_filename
        self.favorites_filename = favorites_filename

        self.captions_to_video_ids: Dict = {}
        self.video_ids_to_captions: Dict = {}
        self.user_ids_to_favorite_captions: Dict = {}

        self.captions_to_video_ids, self.video_ids_to_captions = build_video_dictionaries_from_file(self.videos_filename)
        self.user_ids_to_favorite_captions = build_favorite_dictionary_from_file(self.favorites_filename)

        print(self.user_ids_to_favorite_captions)

    def save_video(self, caption: str, telegram_video_id: str):
        if caption == '':
            return 'El video no incluye ningun caption, no sera guardado.'

        elif len(caption) > 32:
            return 'El caption tiene mas de 32 caracteres. Sube el video con un caption mas corto.'
        
        elif caption in self.captions_to_video_ids:
            return f'Otro video ya usa el caption "{caption}." Sube el video con un caption diferente.'

        self.captions_to_video_ids[caption] = telegram_video_id
        self.video_ids_to_captions[telegram_video_id] = caption

        with open(self.videos_filename, mode='a') as data_file:
            data_file.write(f'\n{caption}={telegram_video_id}')
        return 'Video guardado exitosamente.'

    def get_video_id(self, caption: str) -> str:
        if caption.startswith('⭐'):
            caption = caption[2:]

        return self.captions_to_video_ids.get(caption)

    #TODO: make this work with the Telegram Video unique id, so not only the original video is required to be replied to
    def favorite(self, video_id: str, user_id: str) -> str:
        caption = self.video_ids_to_captions.get(video_id)

        if caption is None:
            return 'Este video no es parte de AudioGif.'
        
        existing_favorites = self.user_ids_to_favorite_captions.get(user_id, [])
        if len(existing_favorites) > 49:
            return 'Solo se permite un maximo de 50 favoritos.'

        caption = f'⭐ {caption}'

        existing_favorites.append(caption)
        self.user_ids_to_favorite_captions[user_id] = existing_favorites
        with open(self.favorites_filename, mode='a') as data_file:
            data_file.write(f'\n{user_id}={caption}')
        
        return 'Favorito guardado exitosamente.'

    def search_video_captions(self, search_query: str, user_id: str) -> List:
        captions: List = list(self.captions_to_video_ids.keys())

        results = self.user_ids_to_favorite_captions.get(user_id, [])
        results.extend(captions)

        if len(search_query) > 2:
            results = list(filter(lambda prompt: search_query in prompt, captions))

        return results[0: self.MAX_VIDEOS_SEARCH_RESULT - 1]
    

def build_video_dictionaries_from_file(filename: str) -> Dict:
    with open(filename, mode='r') as data_file:
        captions_to_video_ids = {}
        video_ids_to_captions = {}

        for line in data_file:
            values = line.split('=')
            if (len(values) < 2):
                continue

            caption = values[0].strip()
            video_id = values[1].strip()

            captions_to_video_ids[caption] = video_id
            video_ids_to_captions[video_id] = caption
        
        return (captions_to_video_ids, video_ids_to_captions)

def build_favorite_dictionary_from_file(filename: str) -> Dict:
    with open(filename, mode='r') as data_file:
        user_ids_to_favorite_captions = {}

        for line in data_file:
            values = line.split('=')
            if (len(values) < 2):
                continue

            user_id = values[0].strip()
            caption = values[1].strip()

            favorites = user_ids_to_favorite_captions.get(user_id, [])
            favorites.append(caption)
            user_ids_to_favorite_captions[user_id] = favorites
        
        return user_ids_to_favorite_captions