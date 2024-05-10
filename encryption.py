import hashlib
import pyAesCrypt
import os


# Function to process the uploaded file
def process_file(filename, password, app):
    # Encryption
    encrypt_file(filename, password, app)
    
    # Sender side Integrity
    calculate_hash(filename, password, app)
    
    # Remove the original text file
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

# Function to encrypt a file
def encrypt_file(filename, password, app):
    bufferSize = 64 * 1024
    input_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_file = os.path.join(app.config['UPLOAD_FOLDER'], filename + '.aes')
    with open(input_file, 'rb') as fIn:
        with open(output_file, 'wb') as fOut:
            pyAesCrypt.encryptStream(fIn, fOut, password, bufferSize)

# Function to calculate hash of a file
def calculate_hash(filename, password, app):
    with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb') as f:
        content = f.read()
        text = content + password.encode()
        sender_hash_object = hashlib.md5(text)
        hash_value = sender_hash_object.hexdigest()
        with open(os.path.join(app.config['UPLOAD_FOLDER'], 'hash.txt'), 'w') as hash_file:
            hash_file.write(hash_value)



# Function to decrypt a file
def decrypt_file(filename, decrypted_filename, password, app):
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