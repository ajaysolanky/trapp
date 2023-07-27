from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import uuid

from pipeline import VideoPipeline, AudioPipeline
from config.valid_languages import ValidISOLanguages

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

    voice_model_name = 'Ajay Solanky'
    language = request.form.get('language')
    if not language:
        return jsonify({"error": "No language selected"}), 500

    print(f"Filename: {file.filename}")
    print(f"Language: {language}")
    print(f"Voice Model Name: {voice_model_name}")

    if os.path.splitext(file.filename)[1].lower() in ['.mp4', '.mov']:
        process_fn = process_video
    else:
        process_fn = process_audio

    if file:
        filename = request.form.get('filename', None)
        if not filename:
            filename = str(uuid.uuid4()) + ".mp4"
        fpath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.isfile(fpath):
            print('File already exists at output path, skipping save in order to use cache')
            file.save(fpath)

        # Here you can call your processing logic
        lang_enum = ValidISOLanguages[language]
        download_url = process_fn(os.path.join(UPLOAD_FOLDER, filename), lang_enum, voice_model_name)

        print(f"DOWNLOAD URL {download_url}")
        return jsonify({"message": "Processed successfully", "download_url": download_url}), 200

    return jsonify({"error": "An error occurred while processing the file"}), 500

@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    return send_from_directory(directory=PROCESSED_FOLDER, filename=filename, as_attachment=True)

def process_video(input_path, language, voice_model_name):
    # This is a placeholder for your video processing logic
    # Use your video processing logic here, save the processed video to the PROCESSED_FOLDER
    # and return the filename of the processed video.
    # For now, let's assume the processed video is the same as the uploaded video.
    # output_path = os.path.join(PROCESSED_FOLDER, os.path.basename(input_path))
    # os.rename(input_path, output_path)
    # return os.path.basename(output_path)
    pipeline = VideoPipeline(input_path, language, voice_model_name)
    return pipeline.run()

def process_audio(input_path, language, voice_model_name):
    pipeline = AudioPipeline(input_path, language, voice_model_name)
    return pipeline.run(local_file=False)

if __name__ == "__main__":
    app.run(debug=True)

# rsync -avz --progress --exclude=.git/ --exclude=venv/ --exclude=resources/ -e "ssh -i dontolliver.pem" trapp/ ec2-user@ec2-3-95-165-71.compute-1.amazonaws.com:~/trapp/
