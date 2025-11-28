from data_loader import load_liked_songs_from_spotify, write_to_sqlite, filter_non_explicit_songs
from playlist_creator import add_songs_to_playlist


def main():

    df = load_liked_songs_from_spotify()
    write_to_sqlite(df, 'spotify_stats.db', 'spotify_statistics')
    filter_non_explicit_songs()

    add_songs_to_playlist()

if __name__ == "__main__":
    main()