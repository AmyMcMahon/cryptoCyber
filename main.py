from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import os
import hashlib
import pyAesCrypt

app = Flask(__name__)

# Configure upload folder and allowed file extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for home page
@app.route("/")
def index():
    return render_template('index.html')

# Route for user page
@app.route("/user")
def user():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('user.html', files=files)

# Route for file upload and processing
@app.route("/upload", methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if file and allowed_file(file.filename):
        password = 'password'  # Hardcoded password
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        process_file(filename, password)
        return redirect(url_for('user'))  # Redirect to user page
    else:
        return jsonify({'error': 'File type not allowed'})

# Function to process the uploaded file
def process_file(filename, password):
    # Encryption
    encrypt_file(filename, password)
    
    # Sender side Integrity
    calculate_hash(filename, password)
    
    # Remove the original text file
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

# Function to encrypt a file
def encrypt_file(filename, password):
    bufferSize = 64 * 1024
    input_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_file = os.path.join(app.config['UPLOAD_FOLDER'], filename + '.aes')
    with open(input_file, 'rb') as fIn:
        with open(output_file, 'wb') as fOut:
            pyAesCrypt.encryptStream(fIn, fOut, password, bufferSize)

# Function to calculate hash of a file
def calculate_hash(filename, password):
    with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb') as f:
        content = f.read()
        text = content + password.encode()
        sender_hash_object = hashlib.md5(text)
        hash_value = sender_hash_object.hexdigest()
        with open(os.path.join(app.config['UPLOAD_FOLDER'], 'hash.txt'), 'w') as hash_file:
            hash_file.write(hash_value)

@app.route("/download/<filename>")
def download(filename):
    password = 'password'  # Hardcoded password
    decrypted_filename = filename.replace('.aes', '')
    decrypted_file_path = os.path.join(app.config['UPLOAD_FOLDER'], decrypted_filename)
    
    # Decrypt the file
    decrypt_file(filename, decrypted_filename, password)
    
    # Authenticate the file
    if authenticate_file(decrypted_file_path):
        return send_file(decrypted_file_path, as_attachment=True)
    else:
        return jsonify({'error': 'File authentication failed'})

# Function to decrypt a file
def decrypt_file(filename, decrypted_filename, password):
    bufferSize = 64 * 1024
    input_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_file = os.path.join(app.config['UPLOAD_FOLDER'], decrypted_filename)
    with open(input_file, 'rb') as fIn:
        with open(output_file, 'wb') as fOut:
            try:
                pyAesCrypt.decryptStream(fIn, fOut, password, bufferSize)
            except ValueError:
                print("Decryption failed")

# Function to authenticate a file using a hash file
def authenticate_file(filename):
    hash_filename = filename + '.hash'
    if not os.path.isfile(hash_filename):
        return False
    
    with open(hash_filename, 'r') as f:
        expected_hash = f.read().strip()

    with open(filename, 'rb') as f:
        content = f.read()
        file_hash = hashlib.md5(content).hexdigest()

    return file_hash == expected_hash

# # Route for downloading processed files
# @app.route('/download/<filename>')
# def download_file(filename):
#     return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run()
