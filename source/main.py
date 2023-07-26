from speech_to_text import SpeechToText
from translate import TranslateOpenAI
from text_to_speech import TextToSpeech

from config.valid_languages import ValidLanguages

# the real workflow should be input audio is passed through Whisper regardless, to convert to English. Then that should be converted out to whatever desired language.

AUDIO_SAMPLE_FPATH = 'resources/ajay_voice_sample_hinglish.mp3'
OUTPUT_LANGUAGE = ValidLanguages.EN
VOICE_MODEL_NAME = 'Ajay Solanky'

# Speech to text
stt = SpeechToText()
english_text = stt.audio_filepath_to_text(
    AUDIO_SAMPLE_FPATH,
    output_language=ValidLanguages.EN
    )

print(f'English text:\n{english_text}')

# Translation
if OUTPUT_LANGUAGE == ValidLanguages.EN:
    translated_text = english_text
else:
    translated_text = TranslateOpenAI().translate_string(
        english_text,
        ValidLanguages.EN,
        OUTPUT_LANGUAGE
        )

print(f'Translated text:\n{translated_text}')

# Text to speech
TextToSpeech(VOICE_MODEL_NAME, OUTPUT_LANGUAGE).get_and_save_voice_generation(translated_text)