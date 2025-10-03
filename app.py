import os
import cv2
from flask import Flask, render_template, request, url_for, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"

# Make sure uploads folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    original = None
    edited = None
    download_url = None

    if request.method == "POST":
        file = request.files.get("image")
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            # Show original after upload
            original = url_for("static", filename=f"uploads/{filename}")

            # If edit button clicked
            if "edit" in request.form:
                img = cv2.imread(filepath)

                # Controls
                alpha = float(request.form.get("contrast", 1.0))  # contrast
                beta = int(request.form.get("brightness", 0))     # brightness
                edited_img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

                # Save edited image
                edited_filename = "edited_" + filename
                edited_path = os.path.join(app.config["UPLOAD_FOLDER"], edited_filename)
                cv2.imwrite(edited_path, edited_img)

                edited = url_for("static", filename=f"uploads/{edited_filename}")
                download_url = url_for("download_file", filename=edited_filename)

    return render_template(
        "index.html",
        original=original,
        edited=edited,
        download_url=download_url
    )

@app.route("/download/<filename>")
def download_file(filename):
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
