from enum import Enum

# value should be and ISO-639-1 language code
class ValidLanguages(Enum):
    EN = 'en'
    HI = 'hi'

def get_full_lang_name(lang_enum):
    record_dict = {
        ValidLanguages.EN: 'English',
        ValidLanguages.HI: 'Hindi'
    }
    return record_dict[lang_enum]