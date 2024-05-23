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
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    current_user,
    logout_user,
)
from flask_session import Session
import os
import modules.encryption as enc
from modules.database import Database
import rsa


app = Flask(__name__)
app.secret_key = "My Secret key"  # Change this to a random string later

# Configure upload folder and allowed file extensions
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"txt"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = Database()
login_manager = LoginManager()
login_manager.login_view = "index"
login_manager.init_app(app)
ALLOWED_EXTENSIONS = {"txt"}
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["DOWNLOAD_FOLDER"] = "downloads"


# Function to check if the file extension is allowed
def allowed_file_type(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@login_manager.user_loader
def load_user(user_id):
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
            return redirect(url_for("user"))
        else:
            return render_template("index.html", errorMsg="Invalid Login")
    return render_template("index.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


# Route for create account page
@app.route("/createAccount", methods=["POST", "GET"])
def create():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        public_key = request.form["publicKey"]
        db.createUser(username, password, public_key)
        return redirect(url_for("user"))
    return render_template("createAccount.html")


# Route for user page
@app.route("/user")
@login_required
def user():
    # aes_files = [file for file in os.listdir(app.config['UPLOAD_FOLDER']) if file.endswith('.aes')]
    user = current_user.username
    files = db.getUsersFiles(user)
    users = db.getAllUsers()
    return render_template("user.html", files=files, users=users)


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
        username = current_user.username
        receiver = request.form["select"]

        receiver_public_key_str = db.getPublicKey(receiver)
        if not receiver_public_key_str:
            return jsonify({"error": "Receiver's public key not found"})

        encrypted_symmetric_key, symmetric_key = enc.make_symmetric_key(
            receiver_public_key_str
        )

        filename = secure_filename(file.filename)
        filePath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        file.save(filePath)
        db.insertFile(username, receiver, filePath, encrypted_symmetric_key)
        enc.process_file(filename, symmetric_key, app)

        return redirect(url_for("user"))  # Redirect to user page

    else:
        return jsonify({"error": "File type not allowed"})


@app.route("/download", methods=["POST", "GET"])
def download():
    filename = request.form["filename"]
    private_key = request.form["private_key"]
    print(filename)
    print(private_key)
    symmetric_key = db.getSymmetricKey(filename)

    decrypted_symmetric_key = rsa.decrypt(
        symmetric_key, rsa.PrivateKey.load_pkcs1(private_key.encode())
    )
    decrypted_filename = filename.replace(".aes", "")
    enc.decrypt_file(filename, decrypted_filename, decrypted_symmetric_key, app)

    if enc.verify_signature(decrypted_filename, app):
        send_file(
            os.path.join(app.config["UPLOAD_FOLDER"], decrypted_filename),
            as_attachment=True,
        )
        return redirect(url_for("user"))
    else:
        return "Signature verification failed."


if __name__ == "__main__":
    app.secret_key = "super secret"
    app.run(port=8000)
