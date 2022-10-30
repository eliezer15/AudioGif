from typing import Set, List
import pickledb

class VideoSearch:
    def __init__(self, data_file: str):
        self.db = pickledb.load(data_file, True)

    def find_video_ids(self, search_term: str) -> Set[str]:
        all_keys = list(self.db.getall())
        search_hits = list(filter(lambda key: search_term in key, all_keys))

        results: Set[str] = set()
        for hit in search_hits:
            video_ids = self.db.lgetall(hit)
            results.update(video_ids)
        
        return results
    
    def add_search_terms(self, video_id: str, search_terms: List[str]) -> None:
        for term in search_terms:
            #PickleDB returns False when getting a key that does not exists
            if not self.db.get(term):
                self.db.lcreate(term)
            self.db.ladd(term, video_id)