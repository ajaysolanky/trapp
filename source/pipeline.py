import os

from speech_to_text import SpeechToText
from translate import TranslateOpenAI
from text_to_speech import TextToSpeech
from video_lipsync import VideoLipsyncGooey, VideoLipsyncReplicate
from config.valid_languages import ValidLanguages
from utilities.utils import convert_video_to_audio

class Pipeline(object):
    def __init__(self, sample_path, output_lang, voice_model_name):
        self.sample_path = sample_path
        self.output_lang = output_lang
        self.voice_model_name = voice_model_name
    
    def run(self):
        sample_file_type = self.sample_path.split('.')[-1]

        # Video to mp3
        if sample_file_type == 'mp4':
            audio_sample_fpath = convert_video_to_audio(self.sample_path)
        elif sample_file_type == 'mp3':
            audio_sample_fpath = self.sample_path
        else:
            raise Exception('file must be either mp3 or mp4')

        # Speech to text
        stt = SpeechToText()
        english_text = stt.audio_filepath_to_text(
            audio_sample_fpath,
            output_language=ValidLanguages.EN
            )

        print(f'English text:\n{english_text}')

        # Translation
        if self.output_lang == ValidLanguages.EN:
            translated_text = english_text
        else:
            translated_text = TranslateOpenAI().translate_string(
                english_text,
                ValidLanguages.EN,
                self.output_lang
                )

        print(f'Translated text:\n{translated_text}')

        # Text to speech
        translated_audio_fpath = 'output/' + os.path.basename(audio_sample_fpath)
        output_audio_fpath = TextToSpeech(self.voice_model_name, self.output_lang).get_and_save_voice_generation(translated_text, translated_audio_fpath)
        print(output_audio_fpath)

        # Video lipsync
        if sample_file_type == 'mp4':
            video_link = VideoLipsyncReplicate.get_download_link_synced_video(self.sample_path, output_audio_fpath)
            print(video_link)

# Pipeline(
#     'resources/ajay_talking_video_5.mp4',
#     ValidLanguages.HI,
#     'Ajay Solanky'
# ).run()
