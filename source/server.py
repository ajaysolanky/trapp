from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import uuid

from pipeline import VideoPipeline, AudioPipeline
from config.valid_languages import ValidISOLanguages
from voice_lab import VoiceLab
from utilities.hash_file import hash_file_from_file_obj

template_dir = os.path.abspath('templates/')
app = Flask(__name__, template_folder=template_dir)

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    print("SERVER REQUEST")
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    voice_id = request.form.get('voice_id')
    language = request.form.get('language')
    if not language:
        return jsonify({"error": "No language selected"}), 500

    print(f"Filename: {file.filename}")
    print(f"Language: {language}")
    print(f"Voice Model Name: {voice_id}")

    if os.path.splitext(file.filename)[1].lower() in ['.mp4', '.mov']:
        process_fn = process_video
    else:
        process_fn = process_audio

    if file:
        file_path = save_file_obj_to_hashed_fname(
            file, UPLOAD_FOLDER)

        # Here you can call your processing logic
        lang_enum = ValidISOLanguages[language]
        download_url = process_fn(file_path, lang_enum, voice_id)

        print(f"DOWNLOAD URL {download_url}")
        return jsonify({"message": "Processed successfully", "download_url": download_url}), 200

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
                file, UPLOAD_FOLDER + '/training_samples/')
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
                file, UPLOAD_FOLDER + '/training_samples/')
            voice_filepaths.append(file_path)

    add_voice_sample(voice_id, voice_filepaths)
    return jsonify({"message": "Success"}), 200


def save_file_obj_to_hashed_fname(file_obj, target_dir):
    content = file_obj.read()
    hash_code = hash_file_from_file_obj(file_obj)
    print(f"hash code: {hash_code}")
    file_ext = os.path.splitext(file_obj.filename)[-1]
    file_path = os.path.join(target_dir, hash_code + file_ext)
    with open(file_path, 'wb') as out_file:
        out_file.write(content)
    return file_path


def add_voice_sample(voice_id, voice_filepaths):
    voice_name = VoiceLab().get_voice_name_for_id(voice_id)
    return VoiceLab().add_samples(voice_name, voice_id, voice_filepaths)


def create_voice(voice_filepaths, voice_name, voice_desc):
    return VoiceLab().create_voice(voice_filepaths, voice_name, voice_desc)


def process_video(input_path, language, voice_id):
    # This is a placeholder for your video processing logic
    # Use your video processing logic here, save the processed video to the PROCESSED_FOLDER
    # and return the filename of the processed video.
    # For now, let's assume the processed video is the same as the uploaded video.
    # output_path = os.path.join(PROCESSED_FOLDER, os.path.basename(input_path))
    # os.rename(input_path, output_path)
    # return os.path.basename(output_path)
    pipeline = VideoPipeline(input_path, language, voice_id)
    return pipeline.run()


def process_audio(input_path, language, voice_id):
    pipeline = AudioPipeline(input_path, language, voice_id)
    return pipeline.run(local_file=False)


if __name__ == "__main__":
    app.run(debug=True)

# rsync -avz --progress --exclude=.git/ --exclude=venv/ --exclude=resources/ -e "ssh -i dontolliver.pem" trapp/ ec2-user@ec2-3-95-165-71.compute-1.amazonaws.com:~/trapp/
