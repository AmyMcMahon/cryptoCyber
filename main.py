from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import os
import encryption as enc


app = Flask(__name__)

# Configure upload folder and allowed file extensions
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"txt"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# Function to check if the file extension is allowed
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Route for home page
@app.route("/")
def index():
    return render_template("index.html")


# Route for user page
@app.route("/user")
def user():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template("user.html", files=files)


@app.route("/admin")
def admin():
    return render_template("admin.html")


# Route for file upload and processing
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"})

    if file and allowed_file(file.filename):
        password = "password"  # Hardcoded password
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        enc.process_file(filename, password, app)
        return redirect(url_for("user"))  # Redirect to user page
    else:
        return jsonify({"error": "File type not allowed"})


@app.route("/download/<filename>")
def download(filename):
    password = "password"  # Hardcoded password
    decrypted_filename = filename.replace(".aes", "")
    decrypted_file_path = os.path.join(app.config["UPLOAD_FOLDER"], decrypted_filename)

    # Decrypt the file
    enc.decrypt_file(filename, decrypted_filename, password)

    # Authenticate the file
    if enc.authenticate_file(decrypted_file_path):
        return send_file(decrypted_file_path, as_attachment=True)
    else:
        return jsonify({"error": "File authentication failed"})


# # Route for downloading processed files
# @app.route('/download/<filename>')
# def download_file(filename):
#     return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == "__main__":
    app.run()
