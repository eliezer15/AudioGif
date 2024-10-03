import unicodedata
import string

def remove_accents_and_punctuation(text: str):
    # Normalize the string to decompose unicode characters
    nfkd_form = unicodedata.normalize('NFKD', text)
    
    # Remove accents
    only_ascii = nfkd_form.encode('ASCII', 'ignore').decode('ASCII')
    
    # Remove punctuation
    no_punctuation = ''.join(char for char in only_ascii if char not in string.punctuation)
    
    return no_punctuation.lower()