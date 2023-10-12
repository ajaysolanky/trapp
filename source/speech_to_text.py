from datetime import datetime
import os
import requests

from utilities.cache import cachethis
from config.valid_languages import ValidISOLanguages


class SpeechToText(object):
    BASE_URL = "https://api.openai.com/v1/audio"
    API_KEY = os.getenv('OPENAI_API_KEY', 'not the token')
    HEADERS = {
        "Authorization": f"Bearer {API_KEY}",
    }
    
    @staticmethod
    @cachethis
    def convert_speech_file_to_text_same_language(filepath, language):
        url = f"{SpeechToText.BASE_URL}/transcriptions"
        with open(filepath, 'rb') as audio_file:
            files = {'file': audio_file}
            data = {'model': 'whisper-1', 'language': language.name}
            response = requests.post(url, headers=SpeechToText.HEADERS, files=files, data=data)
            
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        return response.json()['text']
    
    @staticmethod
    @cachethis
    def convert_speech_file_to_text_and_translate(filepath, out_lang):
        assert out_lang == ValidISOLanguages.EN, "can only convert to English right now"
        url = f"{SpeechToText.BASE_URL}/translations"
        with open(filepath, 'rb') as audio_file:
            files = {'file': audio_file}
            data = {'model': 'whisper-1'}
            response = requests.post(url, headers=SpeechToText.HEADERS, files=files, data=data)
            
        response.raise_for_status()
        return response.json()['text']
    
    def audio_filepath_to_text(self, filepath, input_language=None, output_language=None):
        assert input_language or output_language, "need to specify input or output language"
        if input_language == output_language:
            return SpeechToText.convert_speech_file_to_text_same_language(filepath, input_language)
        else:
            return SpeechToText.convert_speech_file_to_text_and_translate(filepath, output_language)

# print(SpeechToText().audio_filepath_to_text('resources/ajay_voice_sample_hi.mp3', ValidLanguages.HI, ValidLanguages.HI))
