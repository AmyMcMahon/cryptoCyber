import os
import pyAesCrypt
import rsa
import bcrypt


def generate_key():
    public_key, private_key = rsa.newkeys(2048)
    pub_key_str = public_key.save_pkcs1().decode("utf-8")
    pub_key_str = pub_key_str.replace("-----BEGIN RSA PUBLIC KEY-----", "")
    pub_key_str = pub_key_str.replace("-----END RSA PUBLIC KEY-----", "")
    pub_key_str = pub_key_str.strip()
    with open("private_key.pem", "wb") as f:
        f.write(private_key.save_pkcs1())
    return pub_key_str


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed


# Function to process the uploaded file
def process_file(filename, password, app):
    # Encryption
    encrypt_file(filename, password, app)

    # Sender side Integrity
    sign_file(filename, password, app)

    # Remove the original text file
    os.remove(os.path.join(app.config["UPLOAD_FOLDER"], filename))


# Function to encrypt a file
def encrypt_file(filename, password, app):
    bufferSize = 64 * 1024
    input_file = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    output_file = os.path.join(app.config["UPLOAD_FOLDER"], filename + ".aes")
    with open(input_file, "rb") as fIn:
        with open(output_file, "wb") as fOut:
            pyAesCrypt.encryptStream(fIn, fOut, password, bufferSize)


# Function to sign a file with private key
def sign_file(filename, password, app):
    with open(os.path.join(app.config["UPLOAD_FOLDER"], filename), "rb") as f:
        content = f.read()

    # Load private key
    with open("private_key.pem", "rb") as f:
        private_key_data = f.read()
    priv_key = rsa.PrivateKey.load_pkcs1(private_key_data)

    # Sign the content
    signature = rsa.sign(content, priv_key, "SHA-256")

    # Save the signature
    with open(os.path.join(app.config["UPLOAD_FOLDER"], filename + ".sig"), "wb") as f:
        f.write(signature)


# Function to verify signature with public key
def verify_signature(filename, app):
    with open(os.path.join(app.config["UPLOAD_FOLDER"], filename), "rb") as f:
        content = f.read()

    # Load public key
    with open("public_key.pem", "rb") as f:
        public_key_data = f.read()
    pub_key = rsa.PublicKey.load_pkcs1(public_key_data)

    # Load signature
    with open(os.path.join(app.config["UPLOAD_FOLDER"], filename + ".sig"), "rb") as f:
        signature = f.read()

    # Verify the signature
    try:
        rsa.verify(content, signature, pub_key)
        return True
    except rsa.VerificationError:
        return False


# Function to decrypt a file
def decrypt_file(filename, decrypted_filename, password, app):
    bufferSize = 64 * 1024
    input_file = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    output_file = os.path.join(app.config["UPLOAD_FOLDER"], decrypted_filename)
    with open(input_file, "rb") as fIn:
        with open(output_file, "wb") as fOut:
            try:
                pyAesCrypt.decryptStream(fIn, fOut, password, bufferSize)
            except ValueError:
                print("Decryption failed")
