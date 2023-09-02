from typing import List
from dotenv import load_dotenv
from os import environ as env
from video_repository import VideoRepository
from string import punctuation
from telegram import Video as TelegramVideo

load_dotenv()
db_filename = env['DB_FILE']
search_filename = env['SEARCH_FILE']

repo = VideoRepository(db_filename, search_filename)

def main():

    all_videos = repo.get_all_videos()
    #add_title_as_search_term(all_videos)
    add_laugh_emoji_videos(all_videos)

def add_title_as_search_term(all_videos: List):
    for video in all_videos:
        search_terms = get_search_terms_from_title(video.title)  
        telegram_video = TelegramVideo(file_unique_id=video.video_id, file_id='fake', width=1, height=1, duration=1)

        print(repo.save_search_terms(telegram_video, search_terms))

def add_laugh_emoji_videos(all_videos: List):
    search_term = ['😂']
    for video in all_videos:
        print(f'{video.title}: {video.video_id}')

def get_search_terms_from_title(title: str) -> List[str]:
    #1 Strip punctuation from it
    table = str.maketrans(dict.fromkeys(punctuation))
    stripped_title = title.translate(table)

    #2 Split by space
    terms = stripped_title.split() #Split with no arguments splits by whitespace

    #3 Remove one letter words
    filtered_terms = filter(lambda term: len(term) > 1, terms)

    # Finally, remove duplicates
    return list(set(filtered_terms))

if __name__ == '__main__':
    main()