import os
import random
import json
import sys
from tinytag import TinyTag
import spotipy
from spotipy.oauth2 import SpotifyOAuth
# import time # You can uncomment this if you want to add small delays for testing purposes

# --- Configuration (rest of your configuration remains the same) ---
SPOTIPY_CLIENT_ID = 'YOUR_SPOTIPY_CLIENT_ID'
SPOTIPY_CLIENT_SECRET = 'YOUR_SPOTIPY_CLIENT_SECRET'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8888/callback' # IMPORTANT: Must match Spotify App settings exactly

# Path to your local music library
MUSIC_LIBRARY_PATH = 'C:/Users/YourUser/Music' # Adjust for your Windows path

# Cache file for local song data
CACHE_FILE = 'local_music_cache.json'

# Playlist settings
PLAYLIST_NAME = "My Random Local Library Jams"
PLAYLIST_DESCRIPTION = "Randomly generated playlist from my local music library."
PLAYLIST_PUBLIC = False # Set to True for a public playlist, False for private
NUMBER_OF_SONGS_TO_ADD = 10000 # Max is around 10,000 for Spotify playlists

# --- Functions ---

def get_songs_from_local_library_with_cache(library_path, cache_file, force_rescan=False):
    """
    Scans a local music library and extracts song details, with caching.
    Returns a list of dictionaries, each with 'artist', 'title', 'album', 'filepath'.
    The 'filepath' is included to check for file existence when loading from cache.
    Includes progress output for large scans.
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
                    # You can uncomment the line below for more detailed warnings, but it can be noisy
                    # print(f"  Warning: Could not read metadata from {filepath} - {e}")
                    pass # Suppress frequent warnings for unreadable files
            
            # Print progress every 1000 files (adjust as needed)
            if files_scanned_count % 1000 == 0:
                print(f"  Processed {files_scanned_count} files, found {songs_found_count} valid songs.")
                # time.sleep(0.01) # Small delay for observing output, remove in production

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


# --- Rest of the script (authenticate_spotify, create_spotify_playlist, search_and_add_tracks_to_playlist, main execution) remains the same ---
# (Pasting the full script for completeness, but the changes are only in the function above)

def authenticate_spotify():
    """
    Authenticates with the Spotify API using OAuth 2.0 Authorization Code Flow.
    Requires user interaction for the first time to grant permissions.
    """
    scope = "user-read-private playlist-modify-public playlist-modify-private"
    sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                            client_secret=SPOTIPY_CLIENT_SECRET,
                            redirect_uri=SPOTIPY_REDIRECT_URI,
                            scope=scope,
                            cache_path=".spotipyoauthcache")

    print(f"Authenticating with Spotify. Please open the URL in your browser if it doesn't open automatically:")
    sp = spotipy.Spotify(auth_manager=sp_oauth)
    print("Successfully authenticated with Spotify.")
    return sp

def create_spotify_playlist(sp, user_id, name, description, public):
    """
    Creates a new Spotify playlist for the given user.
    """
    print(f"\nAttempting to create playlist: '{name}'...")
    try:
        playlist = sp.user_playlist_create(user=user_id, name=name, public=public, description=description)
        print(f"Playlist '{playlist['name']}' created successfully! ID: {playlist['id']}")
        return playlist
    except spotipy.SpotifyException as e:
        print(f"Error creating playlist: {e}")
        return None

def search_and_add_tracks_to_playlist(sp, playlist_id, local_songs, num_songs_to_add):
    """
    Searches for a random sample of local songs on Spotify and adds them to a playlist.
    """
    if not local_songs:
        print("No songs found in your local library to add.")
        return

    actual_num_to_add = min(num_songs_to_add, len(local_songs), 10000)
    if actual_num_to_add == 0:
        print("No songs to add to the playlist.")
        return

    print(f"\nSelecting {actual_num_to_add} random songs from your local library...")
    if len(local_songs) < actual_num_to_add:
        print(f"Warning: Only {len(local_songs)} unique songs available, reducing target to this number.")
        actual_num_to_add = len(local_songs)

   # Add a new configuration for max songs per artist
    MAX_SONGS_PER_ARTIST = 3 # Or any number you prefer

    print(f"\nSelecting {actual_num_to_add} random songs from your local library with a limit of {MAX_SONGS_PER_ARTIST} songs per artist...")

    # Group songs by artist
    songs_by_artist = {}
    for song in local_songs:
        artist = song['artist']
        if artist not in songs_by_artist:
            songs_by_artist[artist] = []
        songs_by_artist[artist].append(song)

    selected_local_songs = []
    
    # Create a list of all artist keys
    artists = list(songs_by_artist.keys())

    # Shuffle the artists to randomize the order in which we pick from them
    random.shuffle(artists)

    # Iterate through artists, picking up to MAX_SONGS_PER_ARTIST from each
    # until we reach the desired number of songs or run out of unique songs.
    current_artist_idx = 0
    while len(selected_local_songs) < actual_num_to_add and artists:
        artist_name = artists[current_artist_idx % len(artists)]
        artist_songs = songs_by_artist[artist_name]

        # If we haven't already taken MAX_SONGS_PER_ARTIST from this artist
        # and there are still songs left for them
        songs_already_taken_from_artist = sum(1 for s in selected_local_songs if s['artist'] == artist_name)
        
        if songs_already_taken_from_artist < MAX_SONGS_PER_ARTIST and artist_songs:
            # Pick a random song from this artist that hasn't been picked yet
            available_songs_for_artist = [s for s in artist_songs if s not in selected_local_songs]
            
            if available_songs_for_artist:
                song_to_add = random.choice(available_songs_for_artist)
                selected_local_songs.append(song_to_add)
            else:
                # No more unique songs for this artist
                pass
        
        # Move to the next artist (circularly)
        current_artist_idx += 1
        
        # If we've gone through all artists and still need more songs,
        # but couldn't find any new unique ones under the quota, break to avoid infinite loop
        if current_artist_idx >= len(artists) * MAX_SONGS_PER_ARTIST and len(selected_local_songs) < actual_num_to_add:
            # This is a heuristic: if we've cycled through artists a few times
            # and are stuck, it means we can't meet the target with current constraints.
            print("Warning: Could not find enough unique songs while adhering to artist limits. Adding fewer songs.")
            break
            
        # Add a check to prevent infinite loops if we run out of unique songs
        # before reaching actual_num_to_add while still trying to respect the quota
        if len(selected_local_songs) == len(set(frozenset(s.items()) for s in local_songs)): # If all unique songs are picked
            break

    # Now `selected_local_songs` contains your selection respecting the artist limit
    # The rest of the function (Spotify search and add) remains the same


    spotify_track_uris = []
    found_count = 0
    not_found_count = 0

    print(f"Searching Spotify for {len(selected_local_songs)} selected songs (this may take a while)...")
    for i, song in enumerate(selected_local_songs):
        query = f"track:\"{song['title']}\" artist:\"{song['artist']}\""
        try:
            results = sp.search(q=query, type='track', limit=5)

            if results['tracks']['items']:
                best_match = None
                for track in results['tracks']['items']:
                    if track['artists'][0]['name'].lower() == song['artist'].lower():
                        if not best_match:
                            best_match = track
                        if song['album'] and 'album' in track and track['album']['name'].lower() == song['album'].lower():
                            best_match = track
                            break
                
                if best_match:
                    spotify_track_uris.append(best_match['uri'])
                    found_count += 1
                else:
                    not_found_count += 1
            else:
                not_found_count += 1

            if (i + 1) % 100 == 0 or (i + 1) == len(selected_local_songs):
                print(f"  Processed {i + 1} songs. Found {found_count}, not found {not_found_count}.")

        except spotipy.SpotifyException as e:
            print(f"  Error searching for '{song['title']}' by '{song['artist']}': {e}")
        except Exception as e:
            print(f"  An unexpected error occurred for '{song['title']}' by '{song['artist']}': {e}")

    print(f"\nFound {found_count} out of {actual_num_to_add} selected songs on Spotify.")
    print(f"{not_found_count} songs were not found or had no strong match.")

    if not spotify_track_uris:
        print("No Spotify tracks found to add to the playlist. Exiting.")
        return

    added_to_playlist_count = 0
    print("\nAdding tracks to the Spotify playlist...")
    for i in range(0, len(spotify_track_uris), 100):
        batch = spotify_track_uris[i:i + 100]
        try:
            sp.playlist_add_items(playlist_id, batch)
            added_to_playlist_count += len(batch)
            print(f"  Added {added_to_playlist_count}/{len(spotify_track_uris)} tracks to playlist.")
        except spotipy.SpotifyException as e:
            print(f"  Error adding batch of tracks: {e}")
            break
        except Exception as e:
            print(f"  An unexpected error occurred while adding tracks: {e}")
            break

    print(f"\nSuccessfully added {added_to_playlist_count} tracks to your Spotify playlist '{PLAYLIST_NAME}'.")


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

            # Get current user's ID
            user_profile = spotify_client.current_user()
            user_id = user_profile['id']
            print(f"Authenticated as Spotify user: {user_profile['display_name']} (ID: {user_id})")

            # 3. Create a new Spotify playlist
            new_playlist = create_spotify_playlist(
                sp=spotify_client,
                user_id=user_id,
                name=PLAYLIST_NAME,
                description=PLAYLIST_DESCRIPTION,
                public=PLAYLIST_PUBLIC
            )

            if new_playlist:
                # 4. Search for local songs on Spotify and add them to the playlist
                search_and_add_tracks_to_playlist(spotify_client, new_playlist['id'], local_songs_data, NUMBER_OF_SONGS_TO_ADD)
            else:
                print("Could not create the Spotify playlist. Exiting.")

    print("\nScript finished.")