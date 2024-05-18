import sqlite3
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file,
    redirect,
    url_for,
)
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, login_required
from flask_session import Session
import os
import modules.encryption as enc
from modules.database import Database
import rsa


app = Flask(__name__)
app.secret_key = "My Secret key"

# Configure upload folder and allowed file extensions
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"txt"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = Database()
login_manager = LoginManager()
login_manager.init_app(app)

ALLOWED_EXTENSIONS = {"txt"}
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["DOWNLOAD_FOLDER"] = "downloads"


# Function to check if the file extension is allowed
def allowed_file_type(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@login_manager.user_loader
def load_user(user_id):
    print("loading user")
    return db.getUserId(user_id)


# Route for home page
@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if db.check_Login(username, password):
            userToLogin = db.getUser(username)
            login_user(userToLogin, remember=False)
            return render_template("user.html")
        else:
            print("Login failed")
            return render_template("index.html")
    return render_template("index.html")


# Route for create account page
@app.route("/createAccount", methods=["POST", "GET"])
def create():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        public_key, private_key = enc.generate_key()
        db.createUser(username, password, public_key)
        return render_template("index.html", private_key=private_key)

    return render_template("createAccount.html")

# Route for user page
@app.route("/user")
@login_required
def user():
    # aes_files = [file for file in os.listdir(app.config['UPLOAD_FOLDER']) if file.endswith('.aes')]
    user = "test"  # change me ltr
    files = db.getUsersFiles(user)
    users = db.getAllUsers()
    return render_template('user.html', files=files, users=users)


@app.route("/admin")
@login_required
def admin():
    users = db.getAllUsersAdmin()
    files = db.getAllFilesAdmin()
    print(users)
    # error cause password not in db???
    return render_template("admin.html", users=users, files=files)


@app.route("/upload", methods=["POST", "GET"])
@login_required
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"})

    if file and allowed_file_type(file.filename):
        username = "test"
        receiver = request.form["select"]
        
        receiver_public_key_str = db.getPublicKey(receiver)
        if not receiver_public_key_str:
            return jsonify({"error": "Receiver's public key not found"})
        
        receiver_public_key = rsa.PublicKey.load_pkcs1(receiver_public_key_str)
        
        symmetric_key = rsa.randnum.read_random_bits(256)

        # Encrypt the symmetric key with receiver's public key
        encrypted_symmetric_key = rsa.encrypt(symmetric_key, receiver_public_key)
        
        filename = secure_filename(file.filename)
        filePath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        
        file.save(filePath)
        db.insertFile(username, receiver, filePath, encrypted_symmetric_key)
        enc.process_file(filename, password, app)

        return redirect(url_for("user"))  # Redirect to user page

    else:
        return jsonify({"error": "File type not allowed"})

<<<<<<< HEAD

@app.route("/download/<filename>")
@login_required
def download(filename):
    password = "password"  # Hardcoded password
    decrypted_filename = filename.replace(".aes", "")
    decrypted_file_path = os.path.join(app.config["UPLOAD_FOLDER"], decrypted_filename)

    # Decrypt the file
    enc.decrypt_file(filename, decrypted_filename, password, app)

    # Authenticate the file
    if enc.authenticate_file(decrypted_file_path):
        return send_file(decrypted_file_path, as_attachment=True)
    else:
        return jsonify({"error": "File authentication failed"})


# Function to decrypt a file, verify its signature, and download it
@app.route("/decrypt_and_download/<filename>")
@login_required
=======
@app.route('/download/<filename>')
>>>>>>> 2a774b8080c01d2208a2e3c9c788386f13f2ec2f
def decrypt_and_download(filename):
    user = request.args.get('user')
    private_key = request.args.get('private_key')
    symmetric_key = db.getSymmetricKey(user)
    decrypted_symmetric_key = rsa.decrypt(symmetric_key, rsa.PrivateKey.load_pkcs1(private_key.encode()))
    decrypted_filename = filename.replace('.aes', '') 
    enc.decrypt_file(filename, decrypted_filename, decrypted_symmetric_key, app)
    if enc.verify_signature(decrypted_filename, app):
        send_file(os.path.join(app.config['UPLOAD_FOLDER'], decrypted_filename),
                         as_attachment=True)
        return redirect(url_for('user'))
    else:
        return "Signature verification failed."


if __name__ == "__main__":
    app.secret_key = "super secret"
    app.run(port=8000)
