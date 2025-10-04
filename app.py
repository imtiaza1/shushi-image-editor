import os
import cv2
import numpy as np
from flask import Flask, render_template, request, url_for, send_file, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}

# Ensure uploads folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def apply_filters(img, brightness=0, contrast=1.0, grayscale=0, rotate=0, flip=False):
    """Apply all filters to the image"""
    try:
        # Brightness and Contrast
        img = cv2.convertScaleAbs(img, alpha=contrast, beta=brightness)
        
        # Grayscale
        if grayscale > 0:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            img = cv2.addWeighted(img, 1 - grayscale/100, gray, grayscale/100, 0)
        
        # Rotation
        if rotate != 0:
            if rotate == 90:
                img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
            elif rotate == 180:
                img = cv2.rotate(img, cv2.ROTATE_180)
            elif rotate == 270:
                img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        
        # Flip
        if flip:
            img = cv2.flip(img, 1)
        
        return img
    except Exception as e:
        print(f"Error applying filters: {e}")
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    original = None
    edited = None
    download_url = None
    error = None

    if request.method == "POST":
        file = request.files.get("image")
        
        if not file or file.filename == "":
            error = "Please select an image file"
            return render_template("index.html", error=error)
    
        if not allowed_file(file.filename):
            error = "Invalid file type. Please upload PNG, JPG, JPEG, WEBP, or BMP"
            return render_template("index.html", error=error)
        
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{secure_filename(file.filename)}"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            original = url_for("static", filename=f"uploads/{filename}")

            if "edit" in request.form:
                img = cv2.imread(filepath)
                
                if img is None:
                    error = "Failed to process image"
                    return render_template("index.html", error=error, original=original)

                # Get filter values
                brightness = int(request.form.get("brightness", 0))
                contrast = float(request.form.get("contrast", 1.0))
                grayscale = int(request.form.get("grayscale", 0))
                rotate = int(request.form.get("rotate", 0))
                flip = "flip" in request.form

                # Apply filters
                edited_img = apply_filters(img, brightness, contrast, grayscale, rotate, flip)
                
                if edited_img is None:
                    error = "Failed to apply filters"
                    return render_template("index.html", error=error, original=original)

                # Save edited image
                edited_filename = f"edited_{filename}"
                edited_path = os.path.join(app.config["UPLOAD_FOLDER"], edited_filename)
                cv2.imwrite(edited_path, edited_img)

                edited = url_for("static", filename=f"uploads/{edited_filename}")
                download_url = url_for("download_file", filename=edited_filename)

        except Exception as e:
            error = f"An error occurred: {str(e)}"
            print(f"Error: {e}")

    return render_template(
        "index.html",
        original=original,
        edited=edited,
        download_url=download_url,
        error=error
    )

@app.route("/download/<filename>")
def download_file(filename):
    try:
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        if not os.path.exists(path):
            return "File not found", 404
        return send_file(path, as_attachment=True)
    except Exception as e:
        return f"Error downloading file: {str(e)}", 500

@app.route("/api/health")
def health():
    return jsonify({"status": "healthy", "version": "1.0.0"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)