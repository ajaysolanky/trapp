import os
import uuid

from speech_to_text import SpeechToText
from translate import TranslateOpenAI
from text_to_speech import TextToSpeech
from video_lipsync import VideoLipsyncGooey, VideoLipsyncReplicate
from config.valid_languages import ValidISOLanguages
from utilities.utils import convert_mp4_to_mp3, convert_mov_to_mp4
from utilities.file_upload import S3Uploader

class VideoPipeline(object):
    def __init__(self, sample_path, output_lang, voice_model_name):
        self.sample_path = sample_path
        self.output_lang = output_lang
        self.voice_model_name = voice_model_name
    
    def run(self):
        print(f"Sample path: {self.sample_path}")
        print(f"output lang: {self.output_lang}")
        print(f"Voice model name: {self.voice_model_name}")
        # sample_file_name, sample_file_type = os.path.basename(self.sample_path).split('.')
        sample_file_name, sample_file_type = os.path.splitext(self.sample_path)
        sample_file_type = sample_file_type.lower() # this is so hacky, there must be a better way

        #mov to mp3
        print('CONVERTING MOV TO MP3')
        if sample_file_type.lower() == '.mov':
            new_sample_path = sample_file_name + '.mp4'
            convert_mov_to_mp4(self.sample_path, new_sample_path)
            sample_file_type = '.mp4'
        else:
            new_sample_path = self.sample_path

        # mp4 to mp3
        print('EXTRACTING MP3 FROM MP4')
        audio_sample_fpath = convert_mp4_to_mp3(new_sample_path)

        audio_pipeline = AudioPipeline(
            audio_sample_fpath,
            self.output_lang,
            self.voice_model_name
        )

        output_audio_fpath = audio_pipeline.run()

        # Video lipsync
        if sample_file_type == '.mp4':
            return_link = VideoLipsyncGooey.get_download_link_synced_video(new_sample_path, output_audio_fpath)
        else:
            raise Exception("Haven't built a way to return audio link yet")
        
        print(f"Return link: {return_link}")
        return return_link

class AudioPipeline(object):
    def __init__(self, sample_path, output_lang, voice_model_name) -> None:
        self.sample_path = sample_path
        self.output_lang = output_lang
        self.voice_model_name = voice_model_name

    def run(self, local_file=True):
        if not local_file:
            uploader = S3Uploader()
        # Speech to text
        stt = SpeechToText()
        english_text = stt.audio_filepath_to_text(
            self.sample_path,
            output_language=ValidISOLanguages.EN
            )

        print(f'English text:\n{english_text}')

        # Translation
        if self.output_lang == ValidISOLanguages.EN:
            translated_text = english_text
        else:
            translated_text = TranslateOpenAI().translate_string(
                english_text,
                ValidISOLanguages.EN,
                self.output_lang
                )

        print(f'Translated text:\n{translated_text}')

        # Text to speech
        translated_audio_fpath = f'output/translated_to_{self.output_lang.name}_' + os.path.basename(self.sample_path)
        output_audio_fpath = TextToSpeech(self.voice_model_name, self.output_lang).get_and_save_voice_generation(translated_text, translated_audio_fpath)
        if local_file:
            return output_audio_fpath
        else:
            print("CLIENT!!!")
            print(uploader.client)
            return uploader.upload(output_audio_fpath, str(uuid.uuid4()) + ".mp3")
            # raise Exception("Need to implement audio upload")

# print(AudioPipeline(
#     'resources/ajay_talking_video_5.mp4',
#     ValidISOLanguages.HI,
#     'Ajay Solanky'
# ).run(local_file=False))