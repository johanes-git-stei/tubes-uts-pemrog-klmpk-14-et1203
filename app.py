import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import bcrypt
from werkzeug.utils import secure_filename

# Configuration
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"mp4", "avi", "mov", "mkv"}

app = Flask(__name__, template_folder="templates")
app.secret_key = "your_secret_key"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Helper: Check if file extension is allowed
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Route: Home
@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("browse_videos"))
    return render_template("index.html")

# Route: Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password, is_admin FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode(), user[2].encode()):
            session["user"] = {"id": user[0], "username": user[1], "is_admin": user[3]}
            flash("Login successful!", "success")
            return redirect(url_for("browse_videos"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template("login.html")

# Route: Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            flash("Registration successful!", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists.", "danger")
        finally:
            conn.close()

    return render_template("register.html")

# Route: Upload Video
@app.route("/upload", methods=["GET", "POST"])
def upload_video():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        if "file" not in request.files:
            flash("No file selected.", "danger")
            return redirect(request.url)
        file = request.files["file"]

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            # Save video metadata to the database
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO videos (filename, uploader_id) VALUES (?, ?)",
                           (filename, session["user"]["id"]))
            conn.commit()
            conn.close()

            flash("Video uploaded successfully!", "success")
            return redirect(url_for("browse_videos"))

    return render_template("upload.html")

@app.route('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Route: Browse Videos
@app.route("/videos")
def browse_videos():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT videos.id, videos.filename, users.username
        FROM videos
        JOIN users ON videos.uploader_id = users.id
    """)
    videos = cursor.fetchall()
    conn.close()

    return render_template("browse_videos.html", videos=videos)

# Route: Delete Video
@app.route("/delete/<int:video_id>")
def delete_video(video_id):
    if "user" not in session or not session["user"]["is_admin"]:
        flash("Access denied.", "danger")
        return redirect(url_for("browse_videos"))

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT filename FROM videos WHERE id = ?", (video_id,))
    video = cursor.fetchone()

    if video:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], video[0])
        if os.path.exists(filepath):
            os.remove(filepath)

        cursor.execute("DELETE FROM videos WHERE id = ?", (video_id,))
        conn.commit()

    conn.close()
    flash("Video deleted successfully!", "success")
    return redirect(url_for("browse_videos"))

# Route: Download Video
@app.route("/download/<filename>")
def download_video(filename):
    if "user" not in session:
        flash("You need to log in to download videos.", "danger")
        return redirect(url_for("login"))

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(filepath):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)
    else:
        flash("File not found.", "danger")
        return redirect(url_for("browse_videos"))

@app.route("/play/<filename>")
def play_video(filename):
    if "user" not in session:
        flash("You need to log in to play videos.", "danger")
        return redirect(url_for("login"))

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(filepath):
        return render_template("play_video.html", video_url=url_for("uploads", filename=filename))
    else:
        flash("Video not found.", "danger")
        return redirect(url_for("browse_videos"))

# Route: Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))

# Route: Serve uploaded files
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
