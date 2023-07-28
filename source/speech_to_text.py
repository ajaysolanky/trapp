from datetime import datetime
import os
import openai

from utilities.cache import cachethis
from config.valid_languages import ValidISOLanguages

openai.api_key = os.getenv('OPENAI_API_KEY', 'not the token')


class SpeechToText(object):
    @staticmethod
    @cachethis
    def convert_speech_file_to_text_same_language(filepath, language):
        with open(filepath, 'rb') as audio_file:
            result = openai.Audio.transcribe(
                "whisper-1", audio_file, language=language.name)
        return result.to_dict()['text']

    @staticmethod
    @cachethis
    def convert_speech_file_to_text_and_translate(filepath, out_lang):
        assert out_lang == ValidISOLanguages.EN, "can only convert to english right now"
        with open(filepath, 'rb') as audio_file:
            result = openai.Audio.translate("whisper-1", audio_file)
        return result.to_dict()['text']

    def audio_filepath_to_text(self, filepath, input_language=None, output_language=None):
        assert input_language or output_language, "need to specify input or output language"
        if input_language == output_language:
            return SpeechToText.convert_speech_file_to_text_same_language(filepath, input_language)
        else:
            return SpeechToText.convert_speech_file_to_text_and_translate(filepath, output_language)

# print(SpeechToText().audio_filepath_to_text('resources/ajay_voice_sample_hi.mp3', ValidLanguages.HI, ValidLanguages.HI))
