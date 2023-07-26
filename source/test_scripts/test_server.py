import os
import requests

# URL of the Flask server upload endpoint
UPLOAD_URL = "http://127.0.0.1:5000/upload"

def upload_video(video_path):
    with open(video_path, 'rb') as video_file:
        files = {'file': (video_path.split("/")[-1], video_file)}
        data = {'filename': os.path.basename(video_path)}
        response = requests.post(UPLOAD_URL, files=files, data=data)
        
        if response.status_code == 200:
            print("Upload successful!")
            data = response.json()
            print("Message:", data["message"])
            print("Download URL:", data["download_url"])
        else:
            print("Failed to upload video!")
            print("Response:", response.text)

if __name__ == "__main__":
    video_path = "resources/ajay_talking_video_5.mp4"
    upload_video(video_path)
