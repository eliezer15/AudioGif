from asyncore import read
from json import load
import telegram
from dotenv import load_dotenv
from os import environ as env

load_dotenv()
TOKEN = env['TOKEN']

bot = telegram.Bot(TOKEN)

with open('new_videos.txt', 'r+') as new_videos:
    with open(env['VIDEOS_UNIQUE_IDS_FILE'], 'r+') as unique_ids:
        with open(env['VIDEOS_FILE'], 'r') as read_file:
            for line in read_file:
                values = line.split('=')
                if (len(values) < 2):
                    continue

                caption = values[0].strip()
                video_id = values[1].strip()

                print(f'Processing file: {caption} = {video_id}')

                unique_id = bot.get_file(video_id).file_unique_id
                print(f'Saving unique id: {unique_id}\n')

                new_videos.write(f'{caption}={unique_id}\n')
                unique_ids.write(f'{unique_id}={video_id}\n')
