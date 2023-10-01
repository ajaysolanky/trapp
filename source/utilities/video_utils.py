import imageio
import cv2
import moviepy.editor as mpy
import requests
import os

def crop_video_from_bottom(input_path, crop_factor, output_path=None):
    # If no output path is provided, save the video in the same location with a "_cropped" suffix
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = base + "_cropped" + ext

    # Using imageio to crop the video frames
    reader = imageio.get_reader(input_path)
    fps = reader.get_meta_data()['fps']
    temp_output_path = os.path.join(os.path.dirname(output_path), "temp_video.mp4")
    writer = imageio.get_writer(temp_output_path, fps=fps)
    
    # Get the video height
    cap = cv2.VideoCapture(input_path)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    
    # Calculate the amount to crop from the bottom for crop_factor% removal
    crop_bottom = int(height * crop_factor)

    # Process and write each frame after the adjusted cropping
    for frame in reader:
        cropped_frame = frame[:height - crop_bottom, :]
        writer.append_data(cropped_frame)
    writer.close()

    # Using moviepy to merge the audio
    original_video = mpy.VideoFileClip(input_path)
    cropped_video = mpy.VideoFileClip(temp_output_path)
    combined_video = cropped_video.set_audio(original_video.audio)

    # Save the combined video
    combined_video.write_videofile(output_path, codec='libx264', audio_codec='aac')

    # Remove the temporary video
    os.remove(temp_output_path)

    return output_path

def download_video_from_url(url, save_path):
    """Download a video from a URL and save it to a specified path."""
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for HTTP errors

    with open(save_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    return save_path