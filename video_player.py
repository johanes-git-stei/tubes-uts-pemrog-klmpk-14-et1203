import tkinter as tk
from tkinter import filedialog
import vlc
import sys
import datetime

# membuat class untuk aplikasi utama video player menggunakan python-vlc
class videoPlayer:
    def __init__(self, root):
        # initialisasi program utama dan windownya
        self.root = root
        self.root.title("Prototype Video Player") # memberi title window untuk program
        self.root.geometry("1024x576") # memberi ukuran default window

        # VLC player instance
        # I tried my best to reduce lagging/buffering in forward/backward skipping and play/pause, it's not perfect but it is what it is.
        self.instance = vlc.Instance(['--file-caching=10000','--network-caching=10000', '--live-caching=10000','--no-video-title-show', '--avcodec-hw=none'])
        self.player = self.instance.media_player_new() # membuat media player VLC baru

        # membuat frame baru bernama 'top frame' untuk tombol dan volume slider
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(side="top", fill="x") # meletakkan frame di bagian atas window

        # Column and row configuration for top frame
        self.top_frame.grid_columnconfigure(2, weight=1) # memberi bobot agar tombol dan slider volume pada column 0 dan 2 dapat "terdorong" ke kiri dan kanan

        # Add a button to the top frame for opening video file
        open_vid_btn = tk.Button(self.top_frame, text="Open Video File..", height=2, width=16, command = self.open_file)
        open_vid_btn.grid(row = 0, column = 0, padx = (30, 10), pady = (20,10))

        # Add a button to the top frame for closing/ending program
        close_wind_btn = tk.Button(self.top_frame, text="End Program..", height=2, width=14, command = self.on_closing)
        close_wind_btn.grid(row = 0, column = 1, padx = 10, pady = (20,10))

        # Volume slider for controlling volume level
        volume_slider = tk.Scale(self.top_frame, from_=0, to=100, orient="horizontal", length=200, command = self.set_volume)
        volume_slider.set(50)  # Set default volume to 50%
        volume_slider.grid(row=0, column=3, padx=30, pady=10) # Position the volume slider with padding

        # mengatur volume default video di 50
        self.player.audio_set_volume(50)

        # Frame untuk video atau video frame
        self.video_frame = tk.Frame(self.root)
        # Canvas untuk merender video
        self.canvas = tk.Canvas(self.video_frame)
        self.canvas.pack(fill=tk.BOTH, expand=1) # Isi canvas ke kedua arah
        self.video_frame.pack(fill=tk.BOTH, expand=1) # Isi frame video ke kedua arah

        
        # Control frame with buttons
        self.duration_frame = tk.Frame(self.root)
        self.duration_frame.pack(fill = "x") # Letakkan frame di bagian bawah window dan isi secara horizontal

        # Column and row configuration for control frame
        self.duration_frame.grid_columnconfigure(0, weight=1)  # Center horizontally
        # self.duration_frame.grid_columnconfigure(4, weight=1)  # Center horizontally

        # duration slider
        self.duration_slider = tk.Scale(self.duration_frame, from_= 0, to = 100, orient = "horizontal")
        self.duration_slider.grid(row=0, column=0, columnspan = 4, padx = (30,10), pady = 10, sticky = tk.EW) # Posisi slider menggunakan fitur grid, mirip dengan konsep tabel (sort of...)

        # Add countdown timer label
        self.countdown_label = tk.Label(self.duration_frame, text="00:00:00", font=("Helvetica", 14))
        self.countdown_label.grid(row=0, column=4, padx = (10,30), pady = (30,10)) # Posisi label hitung mundur menggunakan fitur grid

        # Control frame with buttons
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack() # Letakkan frame di bawah frame slider durasi

        # Column and row configuration for control frame (change each button column to x+1 if turned on)
        # self.control_frame.grid_columnconfigure(0, weight=1)  # Center horizontally
        # self.control_frame.grid_columnconfigure(4, weight=1)  # Center horizontally

        # Control buttons
        # Tombol untuk mundur 5 detik menggunakan command backward
        # note: bahwa ukuran tombol (height/width) diukur menggunakan satuan "text" (default) dan bukan "pixels"
        backward_btn = tk.Button(self.control_frame, text="<< 5s", height=2, width=10, command = self.backward)
        backward_btn.grid(row=1, column=0, padx= 10, pady=10)

        # Tombol untuk memutar atau menjeda video menggunakan command (atau function) play_pause
        playpause_btn = tk.Button(self.control_frame, text="Play/Pause", height=2, width=10, command = self.play_pause)
        playpause_btn.grid(row=1, column=1, padx=10, pady=10)

        # Tombol untuk maju 5 detik menggunakan command forward
        forward_btn = tk.Button(self.control_frame, text="5s >>", height=2, width=10, command = self.forward)
        forward_btn.grid(row=1, column=2, padx=10, pady=10)

        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Inisialisasi variabel untuk durasi total video
        self.total_duration = 0

    # Fungsi untuk membuka file video dalam python-vlc
    def open_file(self):
        filename = filedialog.askopenfilename() # Dialog untuk memilih file video

        # Set the media in VLC player
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
        
        # Otomatis mulai memutar video menggunakan command/function play_pause
        self.play_pause()

        # Start the countdown timer
        self.update_countdown()

    # Fungsi untuk memutar atau menjeda video
    def play_pause(self):
        if self.player.is_playing():
            self.player.pause()  # Jeda video jika sedang diputar
        else:
            self.player.play()  # Putar video jika sedang dijeda
    
    # Fungsi untuk maju 5 detik
    def forward(self):
        current_time = self.player.get_time()  # Dapatkan waktu pemutaran saat ini dalam milidetik
        new_time = current_time + 5000  # Tambahkan 5000ms (5 detik) ke waktu saat ini
        total_duration = self.player.get_length()  # Dapatkan durasi total video
        if new_time >= total_duration:  # Pastikan waktu baru tidak melebihi durasi video
            new_time = total_duration - 1000  # Sesuaikan waktu agar tidak melewati durasi video
        self.player.set_time(new_time)  # Set waktu pemutaran baru
        
    # Fungsi untuk mundur 5 detik
    def backward(self):
        current_time = self.player.get_time()  # Dapatkan waktu pemutaran saat ini dalam milidetik
        new_time = max(0, current_time - 5000)  # Kurangi 5000ms (5 detik) dan pastikan waktu tidak kurang dari 0
        self.player.set_time(new_time)  # Set waktu pemutaran baru

    # Fungsi untuk mengatur level volume
    def set_volume(self, val):
        volume = int(val)  # Konversi nilai volume menjadi integer
        self.player.audio_set_volume(volume)  # Set level volume pada player

    # Fungsi untuk memformat waktu dalam format jam:menit:detik
    def format_time(self, milliseconds):
        td = datetime.timedelta(milliseconds=milliseconds)  # Konversi milidetik menjadi objek timedelta
        total_seconds = int(td.total_seconds())  # Dapatkan total detik
        hours, remainder = divmod(total_seconds, 3600)  # Hitung jam
        minutes, seconds = divmod(remainder, 60)  # Hitung menit dan detik
        return f"{hours:02}:{minutes:02}:{seconds:02}"  # Format waktu sebagai HH:MM:SS
    
    # Fungsi untuk memperbarui timer saat menghitung mundur
    def update_countdown(self):
        # Dapatkan durasi total video jika belum diatur
        if self.total_duration == 0:
            self.total_duration = self.player.get_length()  # Set durasi total
            if self.total_duration <= 0:  # Jika durasi belum tersedia
                self.root.after(500, self.update_countdown)  # Coba lagi setelah 500ms
                return
            
        if self.player.is_playing():  # Periksa apakah video sedang diputar
            current_time = self.player.get_time()  # Dapatkan waktu pemutaran saat ini
            remaining_time = self.total_duration - current_time  # Hitung waktu tersisa

            if remaining_time < 0:
                remaining_time = 0  # Pastikan waktu tersisa tidak negatif

            time_str = self.format_time(remaining_time)  # Format waktu tersisa
            self.countdown_label.config(text=time_str)  # Perbarui label hitung mundur
        
        # Jadwalkan pembaruan berikutnya setelah 500ms
        self.root.after(500, self.update_countdown)

    # Fungsi untuk menghentikan pemutaran video
    def stop(self):
        self.player.stop()  # Hentikan player

    # Fungsi untuk menghandle event penutupan jendela
    def on_closing(self):
        self.stop()  # Hentikan video sebelum menutup aplikasi
        self.root.destroy()  # Hancurkan jendela utama

# Titik masuk utama untuk aplikasi
if __name__ == "__main__":
    root = tk.Tk()  # Buat jendela utama aplikasi
    app = videoPlayer(root)  # Buat instance pemutar video
    root.mainloop()  # Mulai loop utama untuk aplikasi