````markdown
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
    git clone [https://github.com/fralla2/spotify-local-library-integration-suite.git](https://github.com/fralla2/spotify-local-library-integration-suite.git)
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
10. Click **"Add"** next to the URI, then scroll down and click **"Save"**.

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
```

### Running Spotify\_GeneratePlaylist.py

This script will generate a new Spotify playlist from a random selection of songs in your local library.

```bash
python Spotify_GeneratePlaylist.py
```

### First-time Authentication (for either script):

  * The script will print a URL. Copy and paste this URL into your web browser.
  * You'll be prompted to log in to Spotify and grant permissions to your application.
  * After granting permission, you'll be redirected to your `http://127.0.0.1:8888/callback` URI. Copy the *entire URL* from your browser's address bar and paste it back into your terminal when prompted by `spotipy`.

### Observing Progress:

  * If a full local library scan is performed (first run or `--rescan`), you will see progress updates in the terminal, showing the current directory being scanned and the total number of files processed.
  * The scripts will then proceed with their respective Spotify operations, providing further output.

### Forcing a Full Local Library Rescan

If you've added or removed a significant amount of music from your local library, or if you simply want to refresh the cached data, you can force a full rescan for either script by running it with the `--rescan` argument:

```bash
python Spotify_FollowArtists.py --rescan
# OR
python Spotify_GeneratePlaylist.py --rescan
```

## How It Works

### Local Music Library Caching (`get_songs_from_local_library_with_cache` function):

  * The script first checks for `local_music_cache.json`.
  * If found and valid (less than 10% of cached file paths are missing), it loads song metadata directly from this file, skipping the slow file system scan.
  * If the cache is not found, is invalid, or `--rescan` is used, it performs a full `os.walk` scan of your `MUSIC_LIBRARY_PATH`.
  * During the scan, it uses `tinytag` to extract `artist`, `title`, and `album` from supported audio files.
  * After a full scan, the collected data is saved to `local_music_cache.json` for future use.

### Spotify\_FollowArtists.py Logic:

  * Utilizes the common local library scanning and caching mechanism.
  * Extracts unique artist names from your scanned local library.
  * Authenticates with Spotify using the `user-follow-modify` scope.
  * Searches for each unique artist on Spotify using `sp.search()`.
  * If a strong match is found, it uses `sp.user_follow_artists()` to follow the artist on your Spotify account, handling API batch limits.

### Spotify\_GeneratePlaylist.py Logic:

  * Utilizes the common local library scanning and caching mechanism.
  * Authenticates with Spotify using the `user-read-private`, `playlist-modify-public`, and `playlist-modify-private` scopes.
  * Retrieves your Spotify user ID.
  * Creates a new playlist using `sp.user_playlist_create()`.
  * Randomly selects songs from the (cached or newly scanned) local library.
  * For each selected local song, it performs a Spotify search (`sp.search()`) to find the corresponding track on Spotify, prioritizing matches by artist and album.
  * Adds the found Spotify track URIs to the new playlist in batches of 100 items (`sp.playlist_add_items()`) to adhere to Spotify API limits.

## Limitations and Notes

  * **Spotify Playlist Limit:** Spotify playlists generally have a soft limit of 10,000 tracks. The `Spotify_GeneratePlaylist.py` script will not attempt to add more than this.
  * **Search Accuracy:** Matching local files to Spotify tracks and artists relies on accurate metadata (artist, title, album) in your local files. Misspellings or variations can lead to tracks/artists not being found or incorrect matches.
  * **API Rate Limits:** While `spotipy` handles some rate limiting, very large numbers of searches or follow/add operations can still take a significant amount of time due to Spotify's API rate limits.
  * **Artist Balancing (Requires Implementation in `Spotify_GeneratePlaylist.py`):** The provided code for `Spotify_GeneratePlaylist.py` includes comments for where you would implement the `MAX_SONGS_PER_ARTIST` logic if you choose to. This is not active by default and requires you to uncomment and integrate the suggested code snippet.

## Contributing

Feel free to open issues, submit pull requests, or suggest improvements\!

## License

This project is open-source and available under the [MIT License](https://www.google.com/search?q=LICENSE).

```
```