from db_models import Base, Video, Favorite, User
from dotenv import load_dotenv
from os import environ as env
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
db_filename = env['DB_FILE']

def main():
    engine = create_engine(f'sqlite:///{db_filename}', echo=True)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    video_ids_to_playable_ids = build_dict_from_file('./existing_data/video_unique_ids.txt')
    video_ids_to_captions = build_dict_from_file('./existing_data/videos.txt', True)

    for video_id, playable_id in video_ids_to_playable_ids.items():
        caption = video_ids_to_captions[video_id]
        video = Video(video_id=video_id, playable_video_id=playable_id, title=caption)
        session.add(video)
    
    session.commit()
    
def build_dict_from_file(filename, flip_key_value = False):
    with open(filename, 'r') as data_file:
        result = {}
        for line in data_file:
            values = line.split('=')
            if (len(values) < 2):
                continue
            
            key = values[0].strip()
            value = values[1].strip()

            if flip_key_value:
                result[value] = key
            else:
                result[key] = value
        
        return result

if __name__ == '__main__':
    main()

