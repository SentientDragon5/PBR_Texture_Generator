from flask import Flask, render_template, request, send_from_directory
import os
import pbr_gen  # Import your pbr_gen.py functions
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    image_paths = []
    output_folders = []

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

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(upload_path)
                image_paths.append(upload_path)

                output_folder = os.path.join(app.config['OUTPUT_FOLDER'], os.path.splitext(filename)[0] + '_textures')
                output_folders.append(output_folder)

                pbr_gen.generate_pbr_textures(upload_path, output_folder, albedo_type, normal_type, roughness_type, metallic_type)

        return render_template('index.html', image_paths=image_paths, output_folders=output_folders)

    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/outputs/<path:filename>')
def output_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    app.run(debug=True)