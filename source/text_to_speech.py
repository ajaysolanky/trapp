import os
from enum import Enum
from datetime import datetime
from elevenlabs import set_api_key, voices, generate, save

from utilities.cache import cachethis
from utilities.utils import generate_filename
from config.valid_languages import ValidISOLanguages
from voice_lab import VoiceLab

set_api_key(os.getenv("ELEVEN_LABS_KEY"))


class TTSModels(Enum):
    ELEVEN_LABS = 0


class ElevenModelEnum(Enum):
    ENGLISH = 'eleven_monolingual_v1'
    NONENGLISH = 'eleven_multilingual_v1'


class TextToSpeech(object):
    def __init__(self, voice_id, output_language) -> None:
        self.model = ElevenModelEnum.ENGLISH if output_language == ValidISOLanguages.EN else ElevenModelEnum.NONENGLISH
        self.voice_id = voice_id

    @staticmethod
    @cachethis
    def get_voice_generation_audio(voice_id, model, text):
        # import pdb
        # pdb.set_trace()
        return generate(
            text=text,
            voice=voice_id,
            model=model.value
        )

    def save_voice_generation_audio(self, audio, outpath):
        directory = os.path.dirname(outpath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        save(
            audio,
            outpath
        )
        return outpath

    def get_and_save_voice_generation(self, text, outpath):
        audio = TextToSpeech.get_voice_generation_audio(
            self.voice_id, self.model, text)
        return self.save_voice_generation_audio(audio, outpath)

# TextToSpeech('Ajay Solanky', ElevenModelEnum.ENGLISH).get_and_save_voice_generation('I')
