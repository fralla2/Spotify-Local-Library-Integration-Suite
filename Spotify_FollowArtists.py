import os
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

# --- Functions ---

def get_artists_from_local_library(library_path):
    """
    Scans a local music library and extracts unique artist names.
    """
    artists = set()
    supported_extensions = ('.mp3', '.flac', '.wav', '.m4a', '.ogg', '.wma', '.aiff') # Add more if needed

    print(f"Scanning local music library at: {library_path}")
    for root, _, files in os.walk(library_path):
        for file in files:
            if file.lower().endswith(supported_extensions):
                filepath = os.path.join(root, file)
                try:
                    tag = TinyTag.get(filepath)
                    if tag.artist:
                        artists.add(tag.artist.strip())
                except Exception as e:
                    print(f"Warning: Could not read metadata from {filepath} - {e}")
    print(f"Found {len(artists)} unique artists in your local library.")
    return list(artists)

def authenticate_spotify():
    """
    Authenticates with the Spotify API using OAuth 2.0 Authorization Code Flow.
    Requires user interaction for the first time to grant permissions.
    """
    scope = "user-follow-modify"
    sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                            client_secret=SPOTIPY_CLIENT_SECRET,
                            redirect_uri=SPOTIPY_REDIRECT_URI,
                            scope=scope,
                            cache_path=".spotipyoauthcache") # Stores token for future use

    # This will open a browser window for user authentication
    sp = spotipy.Spotify(auth_manager=sp_oauth)
    print("Successfully authenticated with Spotify.")
    return sp

def search_and_follow_artists(sp, artists_to_follow):
    """
    Searches for artists on Spotify and follows them.
    """
    followed_count = 0
    not_found_count = 0
    already_followed_count = 0
    
    print("\nStarting to search and follow artists on Spotify...")
    for artist_name in artists_to_follow:
        try:
            results = sp.search(q=f'artist:"{artist_name}"', type='artist', limit=1)
            
            if results['artists']['items']:
                spotify_artist = results['artists']['items'][0]
                spotify_artist_id = spotify_artist['id']
                spotify_artist_name = spotify_artist['name']

                # Check if already following (optional, but good practice)
                # Note: spotipy doesn't have a direct 'is_following_artist' method.
                # You'd typically fetch followed artists and check, but for simplicity,
                # the API itself will handle duplicates.
                
                sp.user_follow_artists([spotify_artist_id])
                print(f"  --> Followed: {spotify_artist_name} (ID: {spotify_artist_id})")
                followed_count += 1
            else:
                print(f"  Artist not found on Spotify: {artist_name}")
                not_found_count += 1
        except spotipy.SpotifyException as e:
            if "already follows" in str(e).lower():
                print(f"  Already following: {artist_name}")
                already_followed_count += 1
            else:
                print(f"  Error following {artist_name}: {e}")
        except Exception as e:
            print(f"  An unexpected error occurred for {artist_name}: {e}")

    print(f"\n--- Summary ---")
    print(f"Artists processed: {len(artists_to_follow)}")
    print(f"Artists followed: {followed_count}")
    print(f"Artists already followed: {already_followed_count}")
    print(f"Artists not found on Spotify: {not_found_count}")


# --- Main execution ---
if __name__ == "__main__":
    if SPOTIPY_CLIENT_ID == 'YOUR_SPOTIPY_CLIENT_ID' or SPOTIPY_CLIENT_SECRET == 'YOUR_SPOTIPY_CLIENT_SECRET':
        print("ERROR: Please update SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET in the script with your Spotify App credentials.")
    elif not os.path.exists(MUSIC_LIBRARY_PATH):
        print(f"ERROR: The specified music library path does not exist: {MUSIC_LIBRARY_PATH}")
        print("Please update MUSIC_LIBRARY_PATH in the script to your actual music library location.")
    else:
        # 1. Get artists from local library
        local_artists = get_artists_from_local_library(MUSIC_LIBRARY_PATH)

        if not local_artists:
            print("No artists found in your local music library. Exiting.")
        else:
            # 2. Authenticate with Spotify
            spotify_client = authenticate_spotify()

            # 3. Search and follow artists on Spotify
            search_and_follow_artists(spotify_client, local_artists)

    print("\nScript finished.")