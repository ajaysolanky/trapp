import os
from enum import Enum
from datetime import datetime
from elevenlabs import set_api_key, voices, generate, save

from utilities.cache import cachethis
from utilities.utils import generate_filename
from config.valid_languages import ValidLanguages

set_api_key(os.getenv("ELEVEN_LABS_KEY"))

class TTSModels(Enum):
    ELEVEN_LABS = 0

class ElevenModelEnum(Enum):
    ENGLISH = 'eleven_monolingual_v1'
    NONENGLISH = 'eleven_multilingual_v1'

class TextToSpeech(object):
    def __init__(self, voice_name, output_language) -> None:
        self.voice_name = voice_name
        self.model = ElevenModelEnum.ENGLISH if output_language == ValidLanguages.EN else ElevenModelEnum.NONENGLISH
        self.voice_id = self.get_voice_id(voice_name)

    def get_voice_id(self, voice_name):
        voice_list = voices()
        voice_index = [v.name for v in voice_list].index(voice_name)
        return voice_list[voice_index].voice_id

    @staticmethod
    @cachethis
    def get_voice_generation_audio(voice_id, model, text):
        return generate(
        text=text,
        voice=voice_id,
        model=model.value
        )

    def save_voice_generation_audio(self, audio, outpath):
        # fname = generate_filename(self.voice_name, 'wav')
        # outpath = './output/' + fname

        directory = os.path.dirname(outpath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        save(
            audio,
            outpath
        )
        return outpath
    
    def get_and_save_voice_generation(self, text, outpath):
        audio = TextToSpeech.get_voice_generation_audio(self.voice_id, self.model, text)
        return self.save_voice_generation_audio(audio, outpath)

# TextToSpeech('Ajay Solanky', ElevenModelEnum.ENGLISH).get_and_save_voice_generation('I')
