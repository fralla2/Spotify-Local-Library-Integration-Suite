# Spotify Local Library Integration Suite

A collection of Python scripts to enhance your Spotify experience by integrating with your local music library. This suite includes tools to automatically follow artists from your local collection and to create intelligent, random playlists on Spotify.

## Table of Contents

* [Description](#description)
* [Features](#features)
* [Requirements](#requirements)
* [Installation](#installation)
* [Spotify API Setup](#spotify-api-setup)
* [Configuration](#configuration)
    * [Common Configuration](#common-configuration)
    * [Spotify_FollowArtists.py Configuration](#spotify_followartists.py-configuration)
    * [Spotify_GeneratePlaylist.py Configuration](#spotify_generateplaylist.py-configuration)
* [Usage](#usage)
    * [Running Spotify_FollowArtists.py](#running-spotify_followartists.py)
    * [Running Spotify_GeneratePlaylist.py](#running-spotify_generateplaylist.py)
    * [Forcing a Full Local Library Rescan](#forcing-a-full-local-library-rescan)
* [How It Works](#how-it-works)
    * [Local Music Library Caching](#local-music-library-caching)
    * [Spotify_FollowArtists.py Logic](#spotify_followartists.py-logic)
    * [Spotify_GeneratePlaylist.py Logic](#spotify_generateplaylist.py-logic)
* [Limitations and Notes](#limitations-and-notes)
* [Contributing](#contributing)
* [License](#license)

## Description

Do you have a massive local music collection and wish you could better integrate it with Spotify? This suite of Python scripts helps you do just that!
* **`Spotify_FollowArtists.py`**: Automatically follows artists from your local music library on Spotify.
* **`Spotify_GeneratePlaylist.py`**: Scans your local music directory, extracts song metadata, and then leverages the Spotify Web API to find those tracks and add them to a new, randomly generated playlist in your Spotify account.

Both scripts benefit from intelligent caching of your local library's metadata, making subsequent runs significantly faster.

## Features

* **Local Music Library Scanning:** Reads metadata from common audio formats (`.mp3`, `.flac`, `.wav`, `.m4a`, `.ogg`, `.wma`, `.aiff`).
* **Intelligent Caching:** Stores scanned local song data in a `JSON` file (`local_music_cache.json`) to drastically reduce scan times on subsequent runs.
* **Artist Following (`Spotify_FollowArtists.py`):** Identifies artists from your local library and automatically follows them on Spotify.
* **Spotify Playlist Creation (`Spotify_GeneratePlaylist.py`):** Automatically creates a new playlist on your Spotify account.
* **Random Song Selection (`Spotify_GeneratePlaylist.py`):** Randomly picks a specified number of songs from your local library for the playlist.
* **Artist Balancing (Optional, `Spotify_GeneratePlaylist.py`):** Includes a framework to limit the number of songs by a single artist in the generated playlist, promoting diversity.
* **Progress Output:** Provides real-time updates during the local library scan for large collections.

## Requirements

* Python 3.7+
* `spotipy` library
* `tinytag` library

## Installation

1.  **Clone the repository (or download the scripts):**
    ```bash
    git clone [https://github.com/fralla2/Spotify-Local-Library-Integration-Suite.git](https://github.com/fralla2/Spotify-Local-Library-Integration-Suite.git)
    cd spotify-local-library-integration-suite
    ```

2.  **Install Python dependencies:**
    It's highly recommended to use a virtual environment:
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate

    pip install spotipy tinytag
    ```

## Spotify API Setup

To use these scripts, you need to register an application with Spotify to get API credentials.

1.  **Go to the Spotify Developer Dashboard:** https://developer.spotify.com/dashboard/applications
2.  **Log in** with your Spotify account.
3.  Click on **"Create an app"**.
4.  Fill in the **App Name** and **App Description**. You can use something like "Local Spotify Integrator" and a brief description.
5.  Accept the **Developer Terms of Service**.
6.  Click **"Create"**.
7.  Once your app is created, you'll see your **Client ID** and **Client Secret**. Keep these safe!
8.  Click **"Edit Settings"** for your newly created app.
9.  Under **"Redirect URIs"**, add the following URI:
    ```
    [http://127.0.0.1:8888/callback](http://127.0.0.1:8888/callback)
    ```
    **Important:** Spotify no longer allows `localhost` for security reasons. You *must* use `127.0.0.1`.
10. Click **"Add"** next to the URI, then scroll down and click **"Save"`.

## Configuration

Open the respective Python script files (`Spotify_FollowArtists.py` and `Spotify_GeneratePlaylist.py`) and modify the variables in their `--- Configuration ---` sections.

### Common Configuration

These variables are likely common to both scripts and should be configured in each file:

* **`SPOTIPY_CLIENT_ID`**: Your Spotify application's Client ID.
    ```python
    SPOTIPY_CLIENT_ID = 'YOUR_CLIENT_ID_HERE'
    ```
* **`SPOTIPY_CLIENT_SECRET`**: Your Spotify application's Client Secret.
    ```python
    SPOTIPY_CLIENT_SECRET = 'YOUR_CLIENT_SECRET_HERE'
    ```
* **`SPOTIPY_REDIRECT_URI`**: **Must match the URI you set in the Spotify Developer Dashboard exactly.**
    ```python
    SPOTIPY_REDIRECT_URI = '[http://127.0.0.1:8888/callback](http://127.0.0.1:8888/callback)'
    ```
* **`MUSIC_LIBRARY_PATH`**: The absolute path to your local music library. Use forward slashes or escaped backslashes for Windows paths.
    ```python
    MUSIC_LIBRARY_PATH = 'C:/Users/YourUser/Music' # Example for Windows
    # Or: MUSIC_LIBRARY_PATH = 'C:\\Users\\YourUser\\Music'
    # For macOS/Linux: MUSIC_LIBRARY_PATH = '/Users/youruser/Music'
    ```
* **`CACHE_FILE`**: The name of the JSON file where scanned local music data will be stored.
    ```python
    CACHE_FILE = 'local_music_cache.json'
    ```

### Spotify_FollowArtists.py Configuration

* **`FOLLOW_ARTISTS_BATCH_SIZE`**: The number of artists to attempt to follow in a single Spotify API request. (Spotify API limits apply)
    ```python
    FOLLOW_ARTISTS_BATCH_SIZE = 50 # Max 50 for Spotify API
    ```

### Spotify_GeneratePlaylist.py Configuration

* **`PLAYLIST_NAME`**: The desired name for the new Spotify playlist.
    ```python
    PLAYLIST_NAME = "My Random Local Library Jams"
    ```
* **`PLAYLIST_DESCRIPTION`**: A description for your new Spotify playlist.
    ```python
    PLAYLIST_DESCRIPTION = "Randomly generated playlist from my local music library."
    ```
* **`PLAYLIST_PUBLIC`**: Set to `True` if you want the playlist to be public on Spotify, `False` for private.
    ```python
    PLAYLIST_PUBLIC = False
    ```
* **`NUMBER_OF_SONGS_TO_ADD`**: The target number of songs to add to the playlist. Spotify playlists have a soft limit of around 10,000 tracks.
    ```python
    NUMBER_OF_SONGS_TO_ADD = 10000
    ```
* **`MAX_SONGS_PER_ARTIST` (Optional, requires implementation)**: If you want to limit how many songs a single artist can have in the generated playlist to promote diversity, you'll need to uncomment and implement the "Option 1: Basic Artist Quota" logic as discussed in the script.
    ```python
    # MAX_SONGS_PER_ARTIST = 3 # Uncomment and set a value if you implement the artist balancing logic
    ```

## Usage

1.  **Activate your virtual environment** (if you created one):
    ```bash
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

### Running Spotify_FollowArtists.py

This script will scan your local library for artists and attempt to follow them on Spotify.

```bash
python Spotify_FollowArtists.py