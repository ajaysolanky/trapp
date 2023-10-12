import os
import datetime
import re
from moviepy.editor import *
import subprocess
import imageio_ffmpeg as ffmpeg

def convert_mp4_to_mp3(video_path):
    # Load video file using moviepy
    clip = VideoFileClip(video_path)

    # Extract audio from the video clip
    audio = clip.audio

    # Define the output file path (replace .mp4 with .mp3)
    output_path = video_path.replace('.mp4', '.mp3')

    if os.path.isfile(output_path):
        print('File already exists at output path, returning')
        return output_path

    # Export audio to the output file
    audio.write_audiofile(output_path, codec='mp3')

    # Close the clip
    clip.reader.close()
    audio.reader.close_proc()

    return output_path

def convert_mov_to_mp4(input_path, output_path):
    if os.path.isfile(output_path):
        print('File already exists at output path, returning')
        return output_path

    # Ensure that ffmpeg binary is accessible
    ffmpeg_exe = ffmpeg.get_ffmpeg_exe()

    cmd = [
        ffmpeg_exe,
        "-i", input_path,
        "-vcodec", "copy",
        "-acodec", "copy",
        output_path
    ]

    subprocess.run(cmd)


def generate_filename(input_string, extension):
    # Remove non-alphanumeric characters and replace spaces with underscores
    sanitized_string = re.sub(r'[^a-zA-Z0-9 ]', '', input_string).replace(' ', '_')

    # Get the current timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    # Combine sanitized string with timestamp to create a unique filename
    filename = f"{sanitized_string}_{timestamp}.{extension}"

    return filename

def get_media_duration_seconds(file_path):
    """Get the duration of a media file using moviepy."""
    try:
        if file_path.lower().endswith(('.mp3', '.wav', '.m4a', '.flac')):
            # If it's an audio file
            with AudioFileClip(file_path) as clip:
                return clip.duration
        else:
            # Assume it's a video file otherwise
            with VideoFileClip(file_path) as clip:
                return clip.duration
    except Exception as e:
        print(f"Failed to retrieve duration for {file_path}. Error: {e}")
        return None
