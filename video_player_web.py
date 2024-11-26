# CHANGE THE FILE NAME TO video_player.py WHEN TRYING IT

from flask import Flask, render_template, request, jsonify, send_file
import vlc
import os

app = Flask(__name__)

# VLC player instance
instance = vlc.Instance(['--file-caching=10000', '--network-caching=10000', '--live-caching=10000', '--no-video-title-show', '--avcodec-hw=none'])
player = instance.media_player_new()
current_media = None

# API endpoint to load a video
@app.route('/load', methods=['POST'])
def load_video():
    global current_media
    video_path = request.json.get('video_path')
    if not os.path.exists(video_path):
        return jsonify({"error": "File not found"}), 404

    current_media = instance.media_new(video_path)
    player.set_media(current_media)
    player.play()
    return jsonify({"message": "Video loaded successfully"})

# API endpoint to play/pause
@app.route('/play_pause', methods=['POST'])
def play_pause():
    if player.is_playing():
        player.pause()
    else:
        player.play()
    return jsonify({"playing": player.is_playing()})

# API endpoint to forward
@app.route('/forward', methods=['POST'])
def forward():
    current_time = player.get_time()
    player.set_time(current_time + 5000)  # Forward 5 seconds
    return jsonify({"time": player.get_time()})

# API endpoint to backward
@app.route('/backward', methods=['POST'])
def backward():
    current_time = player.get_time()
    player.set_time(max(current_time - 5000, 0))  # Backward 5 seconds
    return jsonify({"time": player.get_time()})

# API endpoint to set volume
@app.route('/volume', methods=['POST'])
def set_volume():
    volume = request.json.get('volume', 50)  # Default volume is 50%
    player.audio_set_volume(volume)
    return jsonify({"volume": volume})

# API endpoint to get current video state
@app.route('/status', methods=['GET'])
def get_status():
    current_time = player.get_time()
    total_duration = player.get_length()
    is_playing = player.is_playing()

    return jsonify({
        "current_time": current_time,
        "total_duration": total_duration,
        "is_playing": is_playing
    })

# Route to serve the HTML page
@app.route('/play_video')
def play_video():
    return render_template("play_video.html")

if __name__ == '__main__':
    app.run(debug=True)
