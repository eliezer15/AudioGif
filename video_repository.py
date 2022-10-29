from os import environ as env
from typing import Dict, List

class VideoRepository:
    
    MAX_VIDEOS_SEARCH_RESULT = 50

    def __init__(self, videos_filename: str):
        self.videos_filename = videos_filename
        self.captions_to_video_ids: Dict = build_dict_from_file(self.videos_filename)

    def save_video(self, caption: str, telegram_video_id: str):
        if caption == '':
            return 'El video no incluye ningun caption, no sera guardado.'

        elif len(caption) > 32:
            return 'El caption tiene mas de 32 caracteres. Sube el video con un caption mas corto.'
        
        elif caption in self.captions_to_video_ids:
            return f'Otro video ya usa el caption "{caption}." Sube el video con un caption diferente.'

        else:
            self.captions_to_video_ids[caption] = telegram_video_id
            with open(self.videos_filename, mode='a') as data_file:
                data_file.write(f'\n{caption}={telegram_video_id}')
            return 'Video guardado exitosamente.'

    def get_video_id(self, caption: str) -> str:
        return self.captions_to_video_ids[caption]

    def search_video_captions(self, search_query: str) -> List:
        captions: List = list(self.captions_to_video_ids.keys())
        results = captions

        if len(search_query) > 2:
            results = list(filter(lambda prompt: search_query in prompt, captions))

        return results[0: self.MAX_VIDEOS_SEARCH_RESULT - 1]

def build_dict_from_file(filename: str) -> Dict:
    with open(filename, mode='r+') as data_file:
        dict = {}
        for line in data_file:
            values = line.split('=')
            if (len(values) < 2):
                continue
            dict[values[0]] = values[1].strip()
        
        return dict