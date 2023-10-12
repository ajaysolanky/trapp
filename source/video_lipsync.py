import json
import os
# import replicate
from abc import ABC, abstractmethod
import requests
import uuid
import time
import subprocess
from moviepy.editor import *
import imageio_ffmpeg as ffmpeg

from utilities.file_upload import S3UploaderObj
from utilities.cache import cachethis
from config.config import TEMP_FOLDER
from utilities.video_utils import download_video_from_url, crop_video_from_bottom

# TODO: should slow down / speed up video to match length of audio

class VideoLipsync(ABC):
    @abstractmethod
    def get_download_link_synced_video(video_path, audio_path, match_speed=True, flip_video=False):
        pass

# class VideoLipsyncReplicate(VideoLipsync):
#     @staticmethod
#     @cachethis
#     def get_download_link_synced_video(video_path, audio_path, match_speed=True, flip_video=False):
#         output = replicate.run(
#             "devxpy/cog-wav2lip:8d65e3f4f4298520e079198b493c25adfc43c058ffec924f2aefc8010ed25eef",
#             input={
#                 "face": open(video_path, "rb"),
#                 "audio": open(audio_path, "rb"),
#                 "smooth": True
#                 }
#         )
#         return output

class VideoLipsyncGooey(VideoLipsync):
    @staticmethod
    @cachethis
    def get_download_link_synced_video(video_path, audio_path, match_speed=True, flip_video=False):
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
    def get_download_link_synced_video(video_path, audio_path, match_speed=True, flip_video=False):
        MAX_QUERY_TIME = 60*15
        start_time = time.time()
        try:
            # can parallelize this
            audio_ext = os.path.splitext(audio_path)[1]
            audio_link = S3UploaderObj.upload(audio_path, str(uuid.uuid4()) + audio_ext)
            video_ext = os.path.splitext(video_path)[1]
            video_link = S3UploaderObj.upload(video_path, str(uuid.uuid4()) + video_ext)

            endpoint = 'https://api.synclabs.so/video'
            headers = {
                "x-api-key": os.environ['SYNC_KEY'],
                "accept": "application/json",
                "Content-Type": "application/json"
            }
            response = requests.post(endpoint,
                                    json={
                                        "audioUrl": audio_link,
                                        "videoUrl": video_link,
                                        "synergize": True # change to true for 10x speedup w/ quality penalty
                                    },
                                    headers=headers)

            if response.status_code not in [200, 201]:
                raise Exception('Something went wrong with submission')
            
            video_id = response.json()['id']

            # Now we need to poll the API to wait for the processing to complete
            # I'll use a simple loop with sleep for this purpose. Adjust as necessary.
            poll_endpoint = f'https://api.synclabs.so/video/{video_id}'
            while time.time() - start_time < MAX_QUERY_TIME:
                time.sleep(1)
                poll_response = requests.get(poll_endpoint, headers=headers)
                
                if poll_response.status_code != 200:
                    raise Exception('Something went wrong with polling')
                
                if poll_response.json()['status'] == 'COMPLETED':
                    return poll_response.json()['url']
            
            raise Exception('Video processing did not complete in expected time')
        finally:
            print(f"Synchronicity execution time: {time.time() - start_time:.2f} seconds")

        # tmp_filename = str(uuid.uuid4())+'.mp4'
        # tmp_path = os.path.join(TEMP_FOLDER, tmp_filename)
        # download_video_from_url(video_url, tmp_path)
        # cropped_video_path = crop_video_from_bottom(tmp_path, 0.173)
        # return S3UploaderObj.upload(cropped_video_path, tmp_filename)

class SimpleOverlay:
    @staticmethod
    def get_download_link_synced_video(video_path, audio_path, match_speed=True, flip_video=False):
        # Load audio and video clips
        audio = AudioFileClip(audio_path)
        video = VideoFileClip(video_path)

        # Capture original aspect ratio
        original_aspect_ratio = video.size[0] / video.size[1]

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

        # Resize video to maintain the original aspect ratio
        new_height = video.size[1]
        new_width = int(original_aspect_ratio * new_height)
        if flip_video:
            video = video.resize((new_height, new_width))

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
