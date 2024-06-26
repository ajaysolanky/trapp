from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import shutil

from pipeline import VideoPipeline, AudioPipeline
from config.valid_languages import ValidISOLanguages
from config.lipsync_engines import LipsyncEngines
from utilities.utils import get_media_duration_seconds
from voice_lab import VoiceLab
from utilities.hash_file import hash_file_from_fp
from utilities.cache import cachethis
from config.config import UPLOAD_FOLDER, PROCESSED_FOLDER, TEMP_FOLDER

MAX_MEDIA_LEN_SECONDS = 10

template_dir = os.path.abspath('templates/')
app = Flask(__name__, template_folder=template_dir)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    print(f"SERVER REQUEST:\n{request.form}\n{request.files}")
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    voice_id = request.form.get('voice_id')
    language = request.form.get('language')
    generate_transcript = request.form.get('generate_transcript') == 'true'
    use_lip_sync = request.form.get('use_lip_sync', 'true') == 'true'
    # lipsync_engine = request.form.get('lipsync_engine', 'GOOEY')
    if use_lip_sync:
        # lipsync_engine = 'GOOEY'
        lipsync_engine = 'SYNCHRONICITY'
    else:
        lipsync_engine = 'SIMPLE_OVERLAY'

    if not language:
        return jsonify({"error": "No language selected"}), 500

    if not voice_id:
        return jsonify({"error": "No voice_id selected"}), 500

    print(f"Filename: {file.filename}")
    print(f"Language: {language}")
    print(f"Voice Model Name: {voice_id}")
    print(f"Generate Transcript: {generate_transcript}")
    print(f"Lipsync Engine: {lipsync_engine}")

    if file:
        file_path = save_file_obj_to_hashed_fname(
            file, UPLOAD_FOLDER, TEMP_FOLDER)

        media_len = get_media_duration_seconds(file_path)
        assert media_len <= MAX_MEDIA_LEN_SECONDS, f"Media too long, max is {MAX_MEDIA_LEN_SECONDS} seconds"

        lang_enum = ValidISOLanguages[language]
        lipsync_enum = LipsyncEngines[lipsync_engine]
        if os.path.splitext(file.filename)[1].lower() in ['.mp4', '.mov']:
            ret_val = process_video(file_path, lang_enum, voice_id, generate_transcript, lipsync_enum)
        else:
            ret_val = process_audio(file_path, lang_enum, voice_id, generate_transcript)

        response = {"message": "Processed successfully"}
        response.update(ret_val)
        assert "download_url" in response, "download_url not attached"
        print(f"RESPONSE: {response}")
        return jsonify(response), 200

    return jsonify({"error": "An error occurred while processing the file"}), 500


@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    return send_from_directory(directory=PROCESSED_FOLDER, filename=filename, as_attachment=True)


@app.route('/create_voice', methods=['POST'])
def create_voice():
    voice_name = request.form['name']
    description = request.form['description']

    uploaded_files = request.files

    voice_filepaths = []
    for fname, file in uploaded_files.items():
        if file.filename:
            file_path = save_file_obj_to_hashed_fname(
                file, UPLOAD_FOLDER + '/training_samples/', TEMP_FOLDER)
            voice_filepaths.append(file_path)

    voice_id = create_voice(voice_filepaths, voice_name, description)
    return jsonify({"message": "Success", "voice_id": voice_id}), 200

# TODO: easy to have collisions on voice name


@app.route('/add_voice_samples', methods=['POST'])
def add_voice_samples():
    voice_id = request.form['voice_id']

    uploaded_files = request.files

    voice_filepaths = []
    for fname, file in uploaded_files.items():
        if file.filename:
            file_path = save_file_obj_to_hashed_fname(
                file, UPLOAD_FOLDER + '/training_samples/', TEMP_FOLDER)
            voice_filepaths.append(file_path)

    add_voice_sample(voice_id, voice_filepaths)
    return jsonify({"message": "Success"}), 200

@app.route('/add_email_to_waitlist', methods=['POST'])
def add_email_to_waitlist():
    pass

#TODO: doing this for caching, but it's probably adding latency
def save_file_obj_to_hashed_fname(file_obj, target_dir, tmp_dir):
    fp = os.path.join(tmp_dir, file_obj.filename)
    file_obj.save(fp)
    hash_code = hash_file_from_fp(fp)
    print(f"hash code: {hash_code}")
    file_ext = os.path.splitext(file_obj.filename)[-1]
    target_file_path = os.path.join(target_dir, hash_code + file_ext)
    shutil.move(fp, target_file_path)
    return target_file_path
    
    # content = file_obj.read()
    # with open(os.path.join(tmp_dir, file_obj.filename), 'rb')
    # hash_code = hash_file_from_file_obj(file_obj)
    # print(f"hash code: {hash_code}")
    # file_ext = os.path.splitext(file_obj.filename)[-1]
    # file_path = os.path.join(target_dir, hash_code + file_ext)
    # with open(file_path, 'wb') as out_file:
    #     out_file.write(content)
    # return file_path


def add_voice_sample(voice_id, voice_filepaths):
    voice_name = VoiceLab().get_voice_name_for_id(voice_id)
    return VoiceLab().add_samples(voice_name, voice_id, voice_filepaths)


def create_voice(voice_filepaths, voice_name, voice_desc):
    return VoiceLab().create_voice(voice_filepaths, voice_name, voice_desc)


def process_video(input_path, language, voice_id, generate_transcript, lipsync_enum):
    # This is a placeholder for your video processing logic
    # Use your video processing logic here, save the processed video to the PROCESSED_FOLDER
    # and return the filename of the processed video.
    # For now, let's assume the processed video is the same as the uploaded video.
    # output_path = os.path.join(PROCESSED_FOLDER, os.path.basename(input_path))
    # os.rename(input_path, output_path)
    # return os.path.basename(output_path)
    pipeline = VideoPipeline(input_path, language, voice_id, generate_transcript, lipsync_enum)
    return pipeline.run()


def process_audio(input_path, language, voice_id, generate_transcript):
    pipeline = AudioPipeline(input_path, language, voice_id, generate_transcript)
    return pipeline.run(local_file=False)


if __name__ == "__main__":
    app.run(debug=True)

# rsync -avz --progress --exclude=.git/ --exclude=venv/ --exclude=resources/ -e "ssh -i dontolliver.pem" trapp/ ec2-user@ec2-3-95-165-71.compute-1.amazonaws.com:~/trapp/
