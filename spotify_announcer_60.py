import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from gtts import gTTS
import time
import pygame
from io import BytesIO
import random
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QCheckBox
from PyQt5.QtCore import QThread, pyqtSignal
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

# Spotify API credentials
CLIENT_ID = os.getenv("API_KEY")
CLIENT_SECRET = os.getenv("API_SECRET")
REDIRECT_URI = 'http://localhost:8888/callback'

# Initialize Spotify client with authentication
scope = "user-read-playback-state user-modify-playback-state"

# Define a custom cache directory
cache_dir = os.path.expanduser("~/.spotify_announcer")
os.makedirs(cache_dir, exist_ok=True)

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=scope,
    cache_path=os.path.join(cache_dir, ".cache")
))

# Initialize pygame mixer
pygame.mixer.init()

# Background thread for announcements
class AnnouncementThread(QThread):
    status_signal = pyqtSignal(str)  # Signal to update the GUI

    def __init__(self, include_song_titles, include_album_titles, announce_at_start):
        super().__init__()
        self.running = True
        self.previous_artist = None
        self.include_song_titles = include_song_titles
        self.include_album_titles = include_album_titles
        self.announce_at_start = announce_at_start
        self.volume_factor = 0.9
        self.fade_steps = 8
        self.fade_duration = 0.2

    def smooth_volume_change(self, spotify_volume, target_volume):
        step_size = (target_volume - spotify_volume) / self.fade_steps
        step_delay = self.fade_duration / self.fade_steps

        for step in range(self.fade_steps):
            new_volume = int(spotify_volume + step * step_size)
            sp.volume(max(1, min(100, new_volume)))
            time.sleep(step_delay)

        sp.volume(max(1, min(100, target_volume)))

    def play_announcement(self, announcement, spotify_volume):
        reduced_volume = max(1, int(spotify_volume * self.volume_factor))

        # Fade out
        self.smooth_volume_change(spotify_volume, reduced_volume)

        # Generate and play TTS
        tts = gTTS(announcement, lang="en", tld="co.uk")
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)

        alpha = 2.5
        announcement_vol = ((spotify_volume / 100) - 0.1) ** alpha
        pygame.mixer.music.load(mp3_fp, namehint="mp3")
        pygame.mixer.music.set_volume(announcement_vol)
        pygame.mixer.music.play()

        # Wait for the announcement to finish
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        # Fade in
        self.smooth_volume_change(reduced_volume, spotify_volume)

    def run(self):
        while self.running:
            try:
                playback = sp.current_playback()
                if not playback or not playback.get('item'):
                    self.status_signal.emit("No track is currently playing.")
                    time.sleep(5)
                    continue

                device = playback['device']
                spotify_volume = device['volume_percent']

                if playback['is_playing']:
                    track = playback['item']
                    if track['type'] != 'track':
                        time.sleep(5)
                        continue

                    artist = ", ".join(artist['name'] for artist in track['artists'])
                    album = track['album']['name'] if track['album'] and 'name' in track['album'] else "Unknown album"
                    song = track['name'] if track.get('name') else "Unknown song"

                    # Get song duration and progress
                    duration_ms = track['duration_ms']
                    progress_ms = playback['progress_ms']
                    remaining_time = (duration_ms - progress_ms) / 1000  # Convert to seconds

                    if self.announce_at_start:
                        # Announce at the start of the song
                        if self.previous_artist is None or artist != self.previous_artist:
                            options = []

                            if self.include_album_titles:
                                options.append(f"{artist}, from the album {album}.")

                            if self.include_song_titles:
                                options.append(f"{artist}. {song}.")

                            if not options:  # Fallback if no options are selected
                                options.append(f"{artist}.")

                            announcement = random.choice(options)
                            self.play_announcement(announcement, spotify_volume)
                            self.previous_artist = artist
                    else:
                        # Announce at the end of the song
                        if remaining_time > 10:
                            time.sleep(min(remaining_time - 10, 5))  # Sleep until 10 seconds remain
                            continue

                        if self.previous_artist is None or artist != self.previous_artist:
                            options = []

                            if self.include_album_titles:
                                options.append(f"{artist}, from the album {album}.")

                            if self.include_song_titles:
                                options.append(f"{artist}. {song}.")

                            if not options:  # Fallback if no options are selected
                                options.append(f"{artist}.")

                            announcement = random.choice(options)
                            self.play_announcement(announcement, spotify_volume)
                            self.previous_artist = artist

                self.status_signal.emit(f"Listening to Spotify: {track['name']} by {artist}")
                time.sleep(1)  # Check playback status more frequently

            except Exception as e:
                self.status_signal.emit(f"Error: {type(e).__name__} - {str(e)}")
                time.sleep(10)

    def stop(self):
        self.running = False
        self.wait()

# Main application window
class SpotifyAnnouncerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spotify Announcer")
        self.setGeometry(100, 100, 300, 250)

        self.thread = None

        # GUI layout
        self.status_label = QLabel("Spotify Announcer is off.")
        self.toggle_button = QPushButton("Start")
        self.toggle_button.clicked.connect(self.toggle_announcer)

        self.song_checkbox = QCheckBox("Include Song Titles")
        self.album_checkbox = QCheckBox("Include Album Titles")
        self.start_checkbox = QCheckBox("Announce at Start of Song")

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.song_checkbox)
        layout.addWidget(self.album_checkbox)
        layout.addWidget(self.start_checkbox)
        layout.addWidget(self.toggle_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def toggle_announcer(self):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.toggle_button.setText("Start")
            self.status_label.setText("Spotify Announcer is off.")
        else:
            include_song_titles = self.song_checkbox.isChecked()
            include_album_titles = self.album_checkbox.isChecked()
            announce_at_start = self.start_checkbox.isChecked()

            self.thread = AnnouncementThread(include_song_titles, include_album_titles, announce_at_start)
            self.thread.status_signal.connect(self.update_status)
            self.thread.start()

            self.toggle_button.setText("Stop")
            self.status_label.setText("Spotify Announcer is running.")

    def update_status(self, message):
        self.status_label.setText(message)

    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
        event.accept()

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpotifyAnnouncerApp()
    window.show()
    sys.exit(app.exec_())
