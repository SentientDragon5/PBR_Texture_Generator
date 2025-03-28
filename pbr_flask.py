from flask import Flask, render_template, request, send_from_directory, jsonify
import os
import pbr_gen  # Import your pbr_gen.py functions
from werkzeug.utils import secure_filename
import time  # Simulate progress for demonstration
import shutil  # For file and folder operations
import zipfile  # For creating ZIP files

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ZIP_FOLDER = 'zips'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['ZIP_FOLDER'] = ZIP_FOLDER

progress = 0  # Global variable to track progress
latest_generated_folders = []  # List to store paths of the latest generated folders
latest_zip_filename = None  # Global variable to store the name of the latest ZIP file

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    global progress, latest_generated_folders, latest_zip_filename
    latest_generated_folders = []  # Reset the list of latest generated folders
    latest_zip_filename = None  # Reset the ZIP file name
    if request.method == 'POST':
        if 'files[]' not in request.files:
            return render_template('index.html', error='No file part')

        files = request.files.getlist('files[]')
        if not files:
            return render_template('index.html', error='No selected file')

        albedo_type = request.form.get('albedo', 'copy')
        normal_type = request.form.get('normal', 'sobel')
        roughness_type = request.form.get('roughness', 'gaussian')
        metallic_type = request.form.get('metallic', 'hsv')

        progress = 0  # Reset progress
        total_files = len(files)

        for idx, file in enumerate(files):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(upload_path)

                output_folder = os.path.join(app.config['OUTPUT_FOLDER'], os.path.splitext(filename)[0] + '_textures')
                os.makedirs(output_folder, exist_ok=True)

                pbr_gen.generate_pbr_textures(upload_path, output_folder, albedo_type, normal_type, roughness_type, metallic_type)

                latest_generated_folders.append(output_folder)  # Track the generated folder
                progress = int(((idx + 1) / total_files) * 100)  # Update progress

        # Create a ZIP file of the latest generated folders
        if len(latest_generated_folders) == 1:
            # Use the name of the first uploaded file for the ZIP file
            base_name = os.path.basename(latest_generated_folders[0])
            latest_zip_filename = f"{base_name}.zip"
        else:
            # Use a generic name if multiple files are uploaded
            latest_zip_filename = "latest_generated_textures.zip"

        zip_path = os.path.join(app.config['ZIP_FOLDER'], latest_zip_filename)
        with zipfile.ZipFile(zip_path, 'w') as zipf:  # Use zipfile.ZipFile here
            for folder in latest_generated_folders:
                for root, _, files in os.walk(folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, app.config['OUTPUT_FOLDER'])
                        zipf.write(file_path, arcname)

        return jsonify({'status': 'completed', 'zip_path': latest_zip_filename})

    return render_template('index.html')

@app.route('/progress')
def get_progress():
    global progress
    return jsonify({'progress': progress})

@app.route('/download_zip')
def download_zip():
    global latest_zip_filename
    if latest_zip_filename:
        return send_from_directory(app.config['ZIP_FOLDER'], latest_zip_filename, as_attachment=True)
    return jsonify({'error': 'No ZIP file available'}), 404

@app.route('/delete_files', methods=['POST'])
def delete_files():
    global latest_generated_folders, latest_zip_filename
    # Delete the latest generated folders
    for folder in latest_generated_folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    latest_generated_folders = []  # Reset the list

    # Delete the ZIP file
    if latest_zip_filename:
        zip_path = os.path.join(app.config['ZIP_FOLDER'], latest_zip_filename)
        if os.path.exists(zip_path):
            os.remove(zip_path)
    latest_zip_filename = None  # Reset the ZIP file name

    # Delete all files in the uploads folder
    for root, _, files in os.walk(app.config['UPLOAD_FOLDER']):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.exists(file_path):
                os.remove(file_path)

    return jsonify({'status': 'deleted'})

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(ZIP_FOLDER, exist_ok=True)
    app.run(debug=True)