import os
import requests

# URL of the Flask server upload endpoint
BASE_URL = "http://127.0.0.1:5000/"


def upload_video(video_path):
    with open(video_path, 'rb') as video_file:
        files = {'file': (video_path.split("/")[-1], video_file)}
        data = {'filename': os.path.basename(video_path)}
        response = requests.post(BASE_URL + 'upload', files=files, data=data)

        if response.status_code == 200:
            print("Upload successful!")
            data = response.json()
            print("Message:", data["message"])
            print("Download URL:", data["download_url"])
        else:
            print("Failed to upload video!")
            print("Response:", response.text)


def create_voice(filepaths, name, desc):
    files_to_upload = {}
    for path in filepaths:
        file_name = path.split('/')[-1]  # Extract the file name from the path
        files_to_upload[file_name] = open(path, 'rb')

    data = {
        'name': name,
        'description': desc
    }

    print(files_to_upload)

    response = requests.post(BASE_URL + 'create_voice',
                             files=files_to_upload, data=data)

    print(response.text)


def add_samples_to_voice(voice_id, filepaths):
    files_to_upload = {}
    for path in filepaths:
        file_name = path.split('/')[-1]  # Extract the file name from the path
        files_to_upload[file_name] = open(path, 'rb')

    data = {
        'voice_id': voice_id
    }

    print(files_to_upload)

    response = requests.post(BASE_URL + 'add_voice_samples',
                             files=files_to_upload, data=data)

    print(response.text)


# if __name__ == "__main__":
    # video_path = "resources/ajay_talking_video_5.mp4"
    # upload_video(video_path)

    # filepaths = ['resources/ajay_voice_sample_1.mp3']
    # create_voice(filepaths, 'Test Person', "29 year old American male")

    # ajay_voice_id = 'aihrQRwznfxTynGbVlKt'
    # add_samples_to_voice(ajay_voice_id, filepaths)
