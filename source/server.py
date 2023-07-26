from flask import Flask, request, jsonify, send_from_directory
import os
import uuid

from pipeline import Pipeline
from config.valid_languages import ValidLanguages

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

@app.route('/')
def index():
    return "Upload a video using /upload endpoint."

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = request.form.get('filename', None)
        if not filename:
            filename = str(uuid.uuid4()) + ".mp4"
        file.save(os.path.join(UPLOAD_FOLDER, filename))

        # Here you can call your processing logic
        download_url = process_video(os.path.join(UPLOAD_FOLDER, filename))
        
        return jsonify({"message": "Video processed successfully", "download_url": download_url}), 200

    return jsonify({"error": "An error occurred while processing the file"}), 500

@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    return send_from_directory(directory=PROCESSED_FOLDER, filename=filename, as_attachment=True)

def process_video(input_path):
    # This is a placeholder for your video processing logic
    # Use your video processing logic here, save the processed video to the PROCESSED_FOLDER
    # and return the filename of the processed video.
    # For now, let's assume the processed video is the same as the uploaded video.
    # output_path = os.path.join(PROCESSED_FOLDER, os.path.basename(input_path))
    # os.rename(input_path, output_path)
    # return os.path.basename(output_path)
    pipeline = Pipeline(input_path, ValidLanguages.HI, 'Ajay Solanky')
    return pipeline.run()

if __name__ == "__main__":
    app.run(debug=True)
