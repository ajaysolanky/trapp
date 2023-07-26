import os
import datetime
import re
from moviepy.editor import *

def convert_video_to_audio(video_path):
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

def generate_filename(input_string, extension):
    # Remove non-alphanumeric characters and replace spaces with underscores
    sanitized_string = re.sub(r'[^a-zA-Z0-9 ]', '', input_string).replace(' ', '_')

    # Get the current timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    # Combine sanitized string with timestamp to create a unique filename
    filename = f"{sanitized_string}_{timestamp}.{extension}"

    return filename