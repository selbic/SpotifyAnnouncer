# Spotify Announcer App

A Python-based desktop application that enhances your Spotify listening experience by announcing the currently playing 
song, artist, and album through text-to-speech (TTS). This app allows you to choose when and what to announce and 
integrates seamlessly with the Spotify API.

## Features

- Announces song titles, album names, and artist names via TTS.
- Configurable options:
  - Include song titles in announcements.
  - Include album titles in announcements.
  - Announce at the start or end of a song.
- Volume smoothing to ensure announcements don’t interrupt your listening experience.
- Simple GUI for easy control.

## Requirements

- Python 3.7+
- Spotify Premium Account
- The following Python libraries:
  - `spotipy`
  - `gTTS`
  - `pygame`
  - `PyQt5`
  - `python-dotenv`

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/spotify-announcer.git
   cd spotify-announcer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Spotify API credentials**:
   - Create a Spotify Developer account at [Spotify for Developers](https://developer.spotify.com/).
   - Create an app and note down the `Client ID` and `Client Secret`.
   - Set the redirect URI to `http://localhost:8888/callback`.

4. **Configure environment variables**:
   - Create a `.env` file in the project root:
     ```
     API_KEY=your_spotify_client_id
     API_SECRET=your_spotify_client_secret
     ```

## Usage

1. **Run the application**:
   ```bash
   python spotify_announcer.py
   ```

2. **Connect to Spotify**:
   - Log in to Spotify when prompted to authorize the application.

3. **Customize settings**:
   - Use checkboxes to include/exclude song titles and album names.
   - Choose whether to announce at the start or end of songs.

4. **Start/Stop Announcer**:
   - Use the "Start" button to activate the announcer.
   - Use the "Stop" button to deactivate.

## How It Works

- The app listens to the current playback on Spotify using the Spotify Web API.
- TTS announcements are generated with Google Text-to-Speech (`gTTS`) and played using `pygame`.
- A PyQt5-based GUI provides a simple interface to configure and control the announcer.

## Notes

- The app saves Spotify credentials in a cache directory: `~/.spotify_announcer/.cache`.
- Ensure the `.env` file is properly configured before running the app.
- The application requires Spotify Premium for playback state access.

## Future Enhancements

- Add support for multiple languages.
- Enable customization of TTS voice settings.
- Integrate with other music streaming platforms.

## License

This project is licensed under the [MIT License](LICENSE).

---

Feel free to contribute or submit issues on the [GitHub repository](https://github.com/yourusername/spotify-announcer). 
Happy listening! 🎵



