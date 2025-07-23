import os
import random # Not directly used for following, but often useful in related scripts
import json # For JSON caching
import sys # For command-line arguments
from tinytag import TinyTag
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# --- Configuration ---
# Replace with your Spotify App credentials
SPOTIPY_CLIENT_ID = 'YOUR_SPOTIPY_CLIENT_ID'
SPOTIPY_CLIENT_SECRET = 'YOUR_SPOTIPY_CLIENT_SECRET'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8888/callback' # Must match your Spotify App settings

# Path to your local music library
MUSIC_LIBRARY_PATH = 'C:/Users/YourUser/Music' # e.g., 'C:/Users/YourUser/Music' or '/home/YourUser/Music'

# Cache file for local song data (shared with Spotify_GeneratePlaylist.py)
CACHE_FILE = 'local_music_cache.json'

# --- Functions ---

def get_songs_from_local_library_with_cache(library_path, cache_file, force_rescan=False):
    """
    Scans a local music library and extracts song details, with caching.
    Returns a list of dictionaries, each with 'artist', 'title', 'album', 'filepath'.
    The 'filepath' is included to check for file existence when loading from cache.
    Includes progress output for large scans.
    This function is designed to be compatible with both scripts.
    """
    if os.path.exists(cache_file) and not force_rescan:
        print(f"Loading song data from cache file: {cache_file}")
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_songs = json.load(f)
            
            # Basic validation: Check if files still exist from the cached data
            valid_cached_songs = []
            missing_files_count = 0
            for song in cached_songs:
                if 'filepath' in song and os.path.exists(song['filepath']):
                    valid_cached_songs.append(song)
                else:
                    missing_files_count += 1
            
            # If a significant portion of files are missing (e.g., >10%), force rescan
            if len(cached_songs) > 0 and (missing_files_count / len(cached_songs)) > 0.1:
                print(f"More than 10% ({missing_files_count}/{len(cached_songs)}) of cached files are missing. Forcing a full rescan.")
            elif missing_files_count > 0:
                print(f"Loaded {len(valid_cached_songs)} valid songs from cache ({missing_files_count} missing files).")
                return valid_cached_songs
            else:
                print(f"Loaded {len(valid_cached_songs)} valid songs from cache (no missing files detected).")
                return valid_cached_songs

        except json.JSONDecodeError as e:
            print(f"Error reading cache file {cache_file}: {e}. Forcing a full rescan.")
        except Exception as e:
            print(f"An unexpected error occurred while loading cache: {e}. Forcing a full rescan.")

    # If cache not found, invalid, or force_rescan is True, perform full scan
    print(f"Performing a full scan of local music library at: {library_path} (This may take a while for large libraries)")
    all_songs = []
    supported_extensions = ('.mp3', '.flac', '.wav', '.m4a', '.ogg', '.wma', '.aiff')

    files_scanned_count = 0
    songs_found_count = 0
    current_directory_progress = ""
    
    # Iterate over directories and files
    for root, dirs, files in os.walk(library_path):
        # Update current directory if it changes
        if root != current_directory_progress:
            current_directory_progress = root
            print(f"\nScanning directory: {current_directory_progress}")

        for file in files:
            files_scanned_count += 1
            filepath = os.path.join(root, file)
            
            if file.lower().endswith(supported_extensions):
                try:
                    tag = TinyTag.get(filepath)
                    if tag.title and tag.artist:
                        song_info = {
                            'artist': tag.artist.strip(),
                            'title': tag.title.strip(),
                            'album': tag.album.strip() if tag.album else "",
                            'filepath': filepath # Store the full path
                        }
                        all_songs.append(song_info)
                        songs_found_count += 1
                except Exception as e:
                    # print(f"  Warning: Could not read metadata from {filepath} - {e}")
                    pass # Suppress frequent warnings for unreadable files
            
            # Print progress every 1000 files (adjust as needed)
            if files_scanned_count % 1000 == 0:
                print(f"  Processed {files_scanned_count} files, found {songs_found_count} valid songs.")

    print(f"\nFinished scanning. Processed {files_scanned_count} files, found {songs_found_count} songs with title and artist.")

    # Save the scanned data to cache
    if all_songs:
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(all_songs, f, indent=4)
            print(f"Saved {len(all_songs)} songs to cache file: {cache_file}")
        except Exception as e:
            print(f"Error saving data to cache file {cache_file}: {e}")
    else:
        print("No songs found to save to cache.")

    return all_songs

def authenticate_spotify():
    """
    Authenticates with the Spotify API using OAuth 2.0 Authorization Code Flow.
    Requires user interaction for the first time to grant permissions.
    """
    # Scope for following artists
    scope = "user-follow-modify"
    sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                            client_secret=SPOTIPY_CLIENT_SECRET,
                            redirect_uri=SPOTIPY_REDIRECT_URI,
                            scope=scope,
                            cache_path=".spotipyoauthcache") # Stores token for future use

    print(f"Authenticating with Spotify. Please open the URL in your browser if it doesn't open automatically:")
    sp = spotipy.Spotify(auth_manager=sp_oauth)
    print("Successfully authenticated with Spotify.")
    return sp

def search_and_follow_artists(sp, local_songs_data):
    """
    Extracts unique artists from local_songs_data, searches for them on Spotify and follows them.
    """
    unique_artists = set()
    for song in local_songs_data:
        if 'artist' in song and song['artist']:
            unique_artists.add(song['artist'].strip())
    
    artists_to_follow = list(unique_artists)
    print(f"\nFound {len(artists_to_follow)} unique artists from your local library to consider following.")

    followed_count = 0
    not_found_count = 0
    already_followed_count = 0
    
    print("\nStarting to search and follow artists on Spotify...")
    # Spotify API limits following to batches of 50
    batch_size = 50 
    
    for i in range(0, len(artists_to_follow), batch_size):
        batch = artists_to_follow[i:i + batch_size]
        artist_ids_to_follow_in_batch = []
        
        for artist_name in batch:
            try:
                results = sp.search(q=f'artist:"{artist_name}"', type='artist', limit=1)
                
                if results['artists']['items']:
                    spotify_artist = results['artists']['items'][0]
                    spotify_artist_id = spotify_artist['id']
                    spotify_artist_name = spotify_artist['name']
                    
                    # We can't directly check if already followed in a batch efficiently without
                    # fetching all followed artists first. The API will gracefully handle duplicates.
                    artist_ids_to_follow_in_batch.append(spotify_artist_id)
                else:
                    print(f"  Artist not found on Spotify: {artist_name}")
                    not_found_count += 1
            except spotipy.SpotifyException as e:
                print(f"  Error searching for '{artist_name}': {e}")
            except Exception as e:
                print(f"  An unexpected error occurred for '{artist_name}': {e}")

        if artist_ids_to_follow_in_batch:
            try:
                # The API itself will handle if you try to follow an artist you already follow
                sp.user_follow_artists(artist_ids_to_follow_in_batch)
                followed_count += len(artist_ids_to_follow_in_batch)
                print(f"  Followed {len(artist_ids_to_follow_in_batch)} artists in this batch. Total followed: {followed_count}")
            except spotipy.SpotifyException as e:
                # Specific error handling for "already follows" if needed, but batch follow is more robust
                print(f"  Error following batch of artists: {e}")
            except Exception as e:
                print(f"  An unexpected error occurred while following artists: {e}")

    print(f"\n--- Summary ---")
    print(f"Artists processed (from local library): {len(artists_to_follow)}")
    print(f"Artists attempted to follow on Spotify: {followed_count + not_found_count + already_followed_count}") # This is a rough count
    print(f"Artists followed (newly or confirmed): {followed_count}")
    # Note: spotipy's user_follow_artists doesn't return how many were *newly* followed vs. already.
    # The 'already_followed_count' from previous version was based on individual error messages, less reliable in batch.
    print(f"Artists not found on Spotify: {not_found_count}")


# --- Main execution ---
if __name__ == "__main__":
    force_rescan_arg = False
    if '--rescan' in sys.argv:
        force_rescan_arg = True
        print("Forcing a full library rescan due to '--rescan' argument.")

    if SPOTIPY_CLIENT_ID == 'YOUR_SPOTIPY_CLIENT_ID' or SPOTIPY_CLIENT_SECRET == 'YOUR_SPOTIPY_CLIENT_SECRET':
        print("ERROR: Please update SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET in the script with your Spotify App credentials.")
    elif not os.path.exists(MUSIC_LIBRARY_PATH):
        print(f"ERROR: The specified music library path does not exist: {MUSIC_LIBRARY_PATH}")
        print("Please update MUSIC_LIBRARY_PATH in the script to your actual music library location.")
    else:
        # 1. Get songs from local library (with caching)
        local_songs_data = get_songs_from_local_library_with_cache(
            MUSIC_LIBRARY_PATH, CACHE_FILE, force_rescan=force_rescan_arg
        )

        if not local_songs_data:
            print("No suitable songs found in your local music library or cache. Exiting.")
        else:
            # 2. Authenticate with Spotify
            spotify_client = authenticate_spotify()

            # 3. Search and follow artists on Spotify
            search_and_follow_artists(spotify_client, local_songs_data)

    print("\nScript finished.")
