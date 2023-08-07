import os
import uuid
import threading

from speech_to_text import SpeechToText
from transcript_summary import TranscriptSummary
from translate import TranslateOpenAI
from text_to_speech import TextToSpeech
from video_lipsync import VideoLipsyncGooey, VideoLipsyncSynchronicity
from config.valid_languages import ValidISOLanguages
from utilities.utils import convert_mp4_to_mp3, convert_mov_to_mp4
from utilities.file_upload import S3UploaderObj


class VideoPipeline(object):
    def __init__(self, sample_path, output_lang, voice_id, generate_transcript, lipsync_enum):
        self.sample_path = sample_path
        self.output_lang = output_lang
        self.voice_id = voice_id
        self.generate_transcript = generate_transcript
        self.lipsync_enum = lipsync_enum

    def run(self):
        print(f"Sample path: {self.sample_path}")
        print(f"output lang: {self.output_lang}")
        print(f"Voice ID: {self.voice_id}")
        # sample_file_name, sample_file_type = os.path.basename(self.sample_path).split('.')
        sample_file_name, sample_file_type = os.path.splitext(self.sample_path)
        # this is so hacky, there must be a better way
        sample_file_type = sample_file_type.lower()

        # mov to mp3
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
            self.voice_id,
            self.generate_transcript
        )

        audio_pipeline_output = audio_pipeline.run(local_file=True)
        
        output_audio_fpath = audio_pipeline_output["audio_filepath"]

        # Video lipsync
        if sample_file_type == '.mp4':
            return_link = self.lipsync_enum.value.get_download_link_synced_video(
                new_sample_path, output_audio_fpath)
        else:
            raise Exception("Haven't built a way to return audio link yet")

        print(f"Return link: {return_link}")
        return {"download_url": return_link} | audio_pipeline_output

class AudioPipeline(object):
    def __init__(self, sample_path, output_lang, voice_id, generate_transcript) -> None:
        self.sample_path = sample_path
        self.output_lang = output_lang
        self.voice_id = voice_id
        self.generate_transcript = generate_transcript

    def run(self, local_file):
        if not local_file:
            uploader = S3UploaderObj
        # Speech to text
        stt = SpeechToText()
        english_text = stt.audio_filepath_to_text(
            self.sample_path,
            output_language=ValidISOLanguages.EN
        )

        print(f'English text:\n{english_text}')

        if self.generate_transcript:
            summary_result = {}
            def summarizer():
                # hardcoded English for now bc we don't know the input language
                summary = TranscriptSummary().get_summary(english_text, "English")
                summary_result['result'] = summary

            t = threading.Thread(target=summarizer)
            t.start()

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
        translated_audio_fpath = f'output/translated_to_{self.output_lang.name}_' + os.path.basename(
            self.sample_path)
        output_audio_fpath = TextToSpeech(self.voice_id, self.output_lang).get_and_save_voice_generation(
            translated_text, translated_audio_fpath)
        if local_file:
            ret_obj = {"audio_filepath": output_audio_fpath}
        else:
            print("CLIENT!!!")
            print(uploader.client)
            dl_link = uploader.upload(output_audio_fpath, str(uuid.uuid4()) + ".mp3")
            ret_obj = {"download_url": dl_link}
        if self.generate_transcript:
            t.join()
            ret_obj.update({"transcript_summary": summary_result["result"]})
        ret_obj.update({
            "voice_id": self.voice_id,
            "output_lang": self.output_lang.name,
            "english_transcript": english_text,
            "transalated_transcript": translated_text
            })
        return ret_obj

# import pdb; pdb.set_trace()
# print(AudioPipeline(
#     'resources/ajay_talking_video_5.mp4',
#     ValidISOLanguages.HI,
#     'Ajay Solanky'
# ).run(local_file=False, generate_transcript=True))
