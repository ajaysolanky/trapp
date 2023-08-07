import json
import os
# import replicate
from abc import ABC, abstractmethod
import requests
import uuid
import subprocess
from moviepy.editor import *
import imageio_ffmpeg as ffmpeg

from utilities.file_upload import S3UploaderObj
from utilities.cache import cachethis
from config.config import TEMP_FOLDER

# TODO: should slow down / speed up video to match length of audio

class VideoLipsync(ABC):
    @abstractmethod
    def get_download_link_synced_video(video_path, audio_path):
        pass

class VideoLipsyncReplicate(VideoLipsync):
    @staticmethod
    @cachethis
    def get_download_link_synced_video(video_path, audio_path):
        output = replicate.run(
            "devxpy/cog-wav2lip:8d65e3f4f4298520e079198b493c25adfc43c058ffec924f2aefc8010ed25eef",
            input={
                "face": open(video_path, "rb"),
                "audio": open(audio_path, "rb"),
                "smooth": True
                }
        )
        return output

class VideoLipsyncGooey(VideoLipsync):
    @staticmethod
    @cachethis
    def get_download_link_synced_video(video_path, audio_path):
        files = [
            ("input_face", open(video_path, "rb")),
            ("input_audio", open(audio_path, "rb")),
        ]
        payload = {}

        response = requests.post(
            "https://api.gooey.ai/v2/Lipsync/form/",
            headers={
                "Authorization": "Bearer " + os.environ["GOOEY_API_KEY"],
            },
            files=files,
            data={"json": json.dumps(payload)},
        )

        return response.json()['output']['output_video']

class VideoLipsyncSynchronicity(VideoLipsync):
    @staticmethod
    @cachethis
    def get_download_link_synced_video(video_path, audio_path):
        # can parallelize this
        audio_ext = os.path.splitext(audio_path)[1]
        audio_link = S3UploaderObj.upload(audio_path, str(uuid.uuid4()) + audio_ext)
        video_ext = os.path.splitext(video_path)[1]
        video_link = S3UploaderObj.upload(video_path, str(uuid.uuid4()) + video_ext)

        endpoint = 'https://rogue-yogi--wav2lip-2-v0-1-02-generate-sync.modal.run'
        response = requests.post(endpoint, params={"audio_uri": audio_link, "video_uri": video_link})

        if response.status_code == 200:
            return response.json()
        raise Exception('Something went wrong')

class SimpleOverlay:
    @staticmethod
    def get_download_link_synced_video(video_path, audio_path, match_speed=False):
        # Load audio and video clips
        audio = AudioFileClip(audio_path)
        video = VideoFileClip(video_path)

        # Check the durations
        audio_duration = audio.duration
        video_duration = video.duration

        if match_speed:
            # Adjust speed of the video to match the audio duration
            speed_factor = video_duration / audio_duration
            video = video.fx(vfx.speedx, speed_factor)

            # Crop the video if it's still longer after speed adjustment (due to rounding)
            if video.duration > audio_duration:
                video = video.subclip(0, audio_duration)
        else:
            # If video is longer than audio, crop video
            if video_duration > audio_duration:
                video = video.subclip(0, audio_duration)

            # If audio is longer than video, loop the video
            elif audio_duration > video_duration:
                n_loops = int(audio_duration // video_duration) + 1
                video = concatenate_videoclips([video] * n_loops)
                video = video.subclip(0, audio_duration)

        # Set the audio of the video clip to our audio clip
        video = video.set_audio(audio)

        # Write to output file
        output_fn = "synced_" + os.path.basename(video_path)
        video_ext = os.path.splitext(output_fn)[1]
        result_filepath = os.path.join(TEMP_FOLDER, output_fn)
        video.write_videofile(result_filepath, codec="libx264")

        return S3UploaderObj.upload(result_filepath, str(uuid.uuid4()) + video_ext)

# import pdb; pdb.set_trace()
# print(SimpleOverlay.get_download_link_synced_video("resources/ajay_talking_video_5.mp4", "tmp/triple_length.mp3"))

# print(response.status_code, result)
