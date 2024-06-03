import base64
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
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
import os
from modules.database import Database


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
            return jsonify(error="Invalid username or password"), 401
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
        username = secure_filename(request.form["username"])
        password = request.form["password"]
        public_key = request.form["publicKey"]
        signingKey = request.form["signPublicKey"]
        path = os.path.join(app.config["UPLOAD_FOLDER"], username)
        if os.path.exists(path):
            return jsonify(error="Nope"), 400
        try:
            # remove user/folder on failue @derv6464
            db.createUser(username, password, public_key, signingKey)
            os.mkdir(path)
            return render_template("index.html")
        except Exception as e:
            print("failed to make directory or add to db")
            # should change error code to be better lol
            return jsonify(error="Failed to create account"), 400

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
    # error cause password not in db???
    return render_template("admin.html", users=users, files=files)


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify(error="No file part"), 400
    if "encryptedSymmetricKey" not in request.form:
        return jsonify(error="No symmetric key"), 400
    if "select" not in request.form:
        return jsonify(error="No receiver selected"), 400
    if "signedFile" not in request.form:
        return jsonify(error="No signed file"), 400
    file = request.files["file"]
    symmetric_key = request.form["encryptedSymmetricKey"]
    signed_file = request.form["signedFile"]
    receiver = request.form["select"]
    iv = request.form["iv"]

    if file.filename == "":
        return jsonify(error="No selected file"), 400
    if not allowed_file_type(file.filename):
        return jsonify(error="Invalid file type"), 400
    if not db.getPublicKey(receiver):
        return jsonify(error="Receiver not found"), 400

    username = current_user.username
    # gets rid of risk of path traversal :)
    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], username)
    if os.path.exists(save_path):
        file_path = os.path.join(save_path, filename)
        file.save(file_path)
        db.insertFile(username, receiver, file_path, symmetric_key, signed_file, iv)
        return jsonify({"success": True})
    return jsonify(error="Failed to upload file"), 400


@app.route("/getPublicKey", methods=["GET"])
def get_public_key():
    username = request.args.get("user")
    if not username:
        return jsonify(error="No user provided"), 400

    public_key = db.getPublicKey(username)
    if not public_key:
        return jsonify(error="Public key not found"), 400
    return jsonify({"publicKey": public_key})


@app.route("/getEncryptedSymmetricKey", methods=["GET"])
def get_encrypted_symmetric_key():
    id = request.args.get("id")
    print
    symmetric_key, iv = db.getFileKeys(id)
    if symmetric_key:
        return jsonify({"symmetricKey": symmetric_key, "iv": iv})
    else:
        return jsonify(error="Symmetric key not found"), 404


@app.route("/getSignedFile", methods=["GET"])
def get_signed_file():
    id = request.args.get("id")
    user_id = db.getSender(id)
    signed_file = db.getSignedFile(id)
    signingKey = db.getSigningKey(user_id)
    if signed_file:
        return jsonify({"signedFile": signed_file, "key": signingKey})
    else:
        return jsonify(error="Signed file not found"), 404


@app.route("/downloadEncryptedFile", methods=["GET"])
def download_encrypted_file():
    id = request.args.get("id")
    file_path = db.getFilePath(id)

    if os.path.exists(file_path):
        with open(file_path, "rb") as file:
            file_content = file.read()
        file_content_base64 = base64.b64encode(file_content).decode("utf-8")
        return jsonify(
            {
                "fileContent": file_content_base64,
                "fileName": os.path.basename(file_path),
            }
        )
    else:
        return jsonify(error="File not found"), 404


if __name__ == "__main__":
    app.secret_key = "super secret"
    app.run(port=8000)
