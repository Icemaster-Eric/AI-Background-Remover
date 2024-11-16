from flask import Flask, request, send_from_directory, jsonify
import os
from werkzeug.utils import secure_filename
import subprocess
import re


def get_port():
    try:
        # Run the `nest get_port` command and capture the output
        result = subprocess.run(
            ["nest", "get_port"],
            text=True,
            capture_output=True,
            check=True
        )

        # Extract the port number using regex
        match = re.search(r"Port (\d+) is free to use!", result.stdout)

        if match:
            return int(match.group(1))

        else:
            raise ValueError("Port number not found in output.")

    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")

    except ValueError as e:
        print(e)


app = Flask(__name__)


# Configuration
UPLOAD_FOLDER = "images"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=["POST"])
def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        return jsonify({"message": "File uploaded successfully", "url": f"/images/{filename}"})

    return jsonify({"error": f"File type not allowed: {file.filename}"}), 400


@app.route("/images/<filename>", methods=["GET"])
def get_image(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(port=35003)
