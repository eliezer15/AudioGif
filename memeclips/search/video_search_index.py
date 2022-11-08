from typing import Set, List
from service.domain_models import Video
from string import punctuation
import pickledb

class VideoSearchIndex:
    """
    Simple abstraction for an inverted search index.
    """
    def __init__(self, db_file_path: str):
        self.db = pickledb.load(db_file_path, True)

    def find_video_ids(self, search_term: str) -> Set[str]:
        all_keys = list(self.db.getall())
        search_hits = list(filter(lambda key: search_term in key, all_keys))

        results: Set[str] = set()
        for hit in search_hits:
            video_ids = self.db.lgetall(hit)
            results.update(video_ids)
        
        return results

    def add_video_to_search_index(self, video: Video):
        search_terms = self.__get_search_terms_from_title(video.title)
        self.__add_search_terms(video.video_id, search_terms)

    def __add_search_terms(self, video_id: str, search_terms: List[str]) -> None:
        for term in search_terms:
            #PickleDB returns False when getting a key that does not exists
            if not self.db.get(term):
                self.db.lcreate(term)
            self.db.ladd(term, video_id)

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