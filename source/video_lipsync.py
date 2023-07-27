import json
import os
# import replicate
from abc import ABC, abstractmethod

import requests

from utilities.cache import cachethis

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


# print(VideoLipsyncGooey.get_download_link_synced_video("resources/ajay_talking_video_4.mp4", "output/Ajay_Solanky_20230725_235818.wav"))

# print(response.status_code, result)
