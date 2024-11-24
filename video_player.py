import tkinter as tk
from tkinter import filedialog
import vlc
import sys
import datetime

class videoPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Prototype Video Player")
        self.root.geometry("800x600")

        # VLC player instance
        # I tried my best to reduce lagging/buffering in forward/backward video skipping, it's not perfect but it is what it is.
        self.instance = vlc.Instance(['--file-caching=10000','--network-caching=10000', '--live-caching=10000','--no-video-title-show', '--avcodec-hw=none'])
        self.player = self.instance.media_player_new()

        # Create the top frame
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(side="top", fill="x")

        # Column and row configuration for top frame
        self.top_frame.grid_columnconfigure(1, weight=1)  # Center horizontally

        # Add a button and slider to the top frame
        top_button = tk.Button(self.top_frame, text="Open Video File..", height=2, width=12, command = self.open_file)
        top_button.grid(row=0, column=0, padx=(30, 10), pady=(20,10))

        # Volume slider
        volume_slider = tk.Scale(self.top_frame, from_=0, to=100, orient="horizontal", length=200, command = self.set_volume)
        volume_slider.set(50)  # Set default volume to 50%
        volume_slider.grid(row=0, column=2, padx=30, pady=10)

        # Set default volume
        self.player.audio_set_volume(50)

        # Video frame
        self.video_frame = tk.Frame(self.root)
        self.canvas = tk.Canvas(self.video_frame)
        self.canvas.pack(fill=tk.BOTH, expand=1)
        self.video_frame.pack(fill=tk.BOTH, expand=1)
        
        # Control frame with buttons
        self.duration_frame = tk.Frame(self.root)
        self.duration_frame.pack(fill = "x")

        # Column and row configuration for control frame
        self.duration_frame.grid_columnconfigure(0, weight=1)  # Center horizontally
        # self.duration_frame.grid_columnconfigure(4, weight=1)  # Center horizontally

        # duration slider
        self.duration_slider = tk.Scale(self.duration_frame, from_= 0, to = 100, orient = "horizontal")
        self.duration_slider.grid(row=0, column=0, columnspan = 4, padx = (30,10), pady = 10, sticky = tk.EW)

        # Add countdown timer label
        self.countdown_label = tk.Label(self.duration_frame, text="00:00:00", font=("Helvetica", 14))
        self.countdown_label.grid(row=0, column=4, padx = (10,30), pady = (30,10))

        # Control frame with buttons
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack()

        # Column and row configuration for control frame (change each button column to x+1 if turned on)
        # self.control_frame.grid_columnconfigure(0, weight=1)  # Center horizontally
        # self.control_frame.grid_columnconfigure(4, weight=1)  # Center horizontally

        # Control buttons
        backward_btn = tk.Button(self.control_frame, text="<< 5s", height=2, width=10, command = self.backward)
        backward_btn.grid(row=1, column=0, padx= 10, pady=10)

        playpause_btn = tk.Button(self.control_frame, text="Play/Pause", height=2, width=10, command = self.play_pause)
        playpause_btn.grid(row=1, column=1, padx=10, pady=10)

        forward_btn = tk.Button(self.control_frame, text="5s >>", height=2, width=10, command = self.forward)
        forward_btn.grid(row=1, column=2, padx=10, pady=10)

        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initialize variables
        self.total_duration = 0

    def open_file(self):
        filename = filedialog.askopenfilename()

        # Set the media
        media = self.instance.media_new(filename)
        self.player.set_media(media)

        # Set the video output window
        os_name = sys.platform
        if os_name == "win32": # Windows OS
            self.player.set_hwnd(self.video_frame.winfo_id())
        elif os_name == "darwin": # Unix-like OS seperti MacOS, iOS, etc.
            self.player.set_nsobject(self.video_frame.winfo_id())
        elif os_name == "linux": # Linux-based OS like Ubuntu, Fedora, etc.
            self.player.set_xwindow(self.video_frame.winfo_id())
        
        self.play_pause()

        # Start the countdown timer
        self.update_countdown()

    def play_pause(self):
        if self.player.is_playing():
            self.player.pause()
        else:
            self.player.play()
    
    def forward(self):
        current_time = self.player.get_time()
        new_time = current_time + 5000  # Skip forward 5000ms = 5 seconds
        total_duration = self.player.get_length()
        if new_time >= total_duration:
            new_time = total_duration - 1000  # Prevent going beyond the video duration
        self.player.set_time(new_time)
        
    def backward(self):
        current_time = self.player.get_time()
        new_time = max(0, current_time - 5000)  # Ensure time doesn't go below 0
        self.player.set_time(new_time)

    def set_volume(self, val):
        volume = int(val)
        self.player.audio_set_volume(volume)

    def format_time(self, milliseconds):
        td = datetime.timedelta(milliseconds=milliseconds)
        # Get total seconds
        total_seconds = int(td.total_seconds())
        # Calculate hours, minutes, and seconds
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        # Format the time string
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    
    def update_countdown(self):
        # Get total duration if not already set
        if self.total_duration == 0:
            self.total_duration = self.player.get_length()
            # If total duration is still not available, try again later
            if self.total_duration <= 0:
                self.root.after(500, self.update_countdown)
                return
            
        if self.player.is_playing():
                current_time = self.player.get_time()
                remaining_time = self.total_duration - current_time

                if remaining_time < 0:
                    remaining_time = 0

                # Format the remaining time using datetime module
                time_str = self.format_time(remaining_time)
                # Update the countdown label
                self.countdown_label.config(text=time_str)
        else:
            # If video is paused, keep the remaining time displayed
            pass

        # Schedule the next update
        self.root.after(500, self.update_countdown)

    def stop(self):
        self.player.stop()

    def on_closing(self):
        self.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = videoPlayer(root)
    root.mainloop()