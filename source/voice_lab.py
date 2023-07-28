from elevenlabs import set_api_key, voices, generate, save, clone
import requests
import os

set_api_key(os.getenv("ELEVEN_LABS_KEY"))


class VoiceLab(object):
    def create_voice(self, voice_filepaths, voice_name, voice_desc):
        args = {
            "name": voice_name,
            "files": voice_filepaths,
        }
        if voice_desc:
            args["description"] = voice_desc

        new_voice = clone(**args)
        return new_voice.voice_id

    def get_voice_id_for_name(self, voice_name):
        voice_list = voices()
        voice_index = [v.name for v in voice_list].index(voice_name)
        return voice_list[voice_index].voice_id

    def get_voice_name_for_id(self, voice_id):
        voice_list = voices()
        voice_index = [v.voice_id for v in voice_list].index(voice_id)
        return voice_list[voice_index].name

    def add_samples(self, voice_name, voice_id, voice_filepaths):
        url = f'https://api.elevenlabs.io/v1/voices/{voice_id}/edit'

        headers = {
            'accept': 'application/json',
            'xi-api-key': os.getenv("ELEVEN_LABS_KEY"),
        }

        # Let's adjust the file_tuples to include the content type
        file_tuples = [('files', (os.path.basename(fp), open(fp, 'rb'), 'audio/mpeg'))
                       for fp in voice_filepaths]

        files = dict(file_tuples)

        # The form data with the string values
        data = {
            'name': voice_name,
            # Add any other fields like 'description' and 'labels' if needed
        }

        response = requests.post(url, headers=headers, data=data, files=files)

        # Make sure you close the opened files
        for _, file_obj, _ in files.values():
            file_obj.close()

        print(response.text)


# print(VoiceLab().get_voice_id_for_name('Aalhad Patankar'))
