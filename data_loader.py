import boto3
import pandas as pd
from io import StringIO
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from spotify_auth import get_spotify_client
import sqlite3


def load_liked_songs_from_spotify() -> pd.DataFrame:
    """
    Creates conection to AWS using boto3, retrieves csv data from my-spotify-stats-bucket, use pandas to create data frame

    Args:
        bucket_name (str): name of bucket we are getting csv data from
        file_name (str): name of csv file
    
    Returns:
        pd.DataFrame: a pandas dataframe containing the csv data.
    """
    #creates s3 client object
    # s3 = boto3.client("s3")

    # response = s3.get_object(Bucket=bucket_name, Key=file_name)
    # csv_data = response['Body'].read().decode('utf-8') #decode utf-8 makes response body a string instead of bytes (original format)

    # #csv_content passed through String_IO because pd.read_csv expects a file or file-like object (not a string or bytes)
    # df = pd.read_csv(StringIO(csv_data))
    sp = get_spotify_client()
    results = sp.current_user_saved_tracks(limit=50)

    rows = []
    for item in results["items"]:
        track = item["track"]
        rows.append({
            "track_name": track["name"],
            "artist": track["artists"][0]["name"],
            "explicit": track["explicit"],
            "duration_ms": track["duration_ms"],
            "popularity": track["popularity"]
        })
    df = pd.DataFrame(rows)

    return df


def write_to_sqlite(df, database_name: str, table_name: str):
    """
    Writes the data frame to a local SQLite database.

    Args:
        df (pd.DataFrame): The data frame to write.
        db_name (str): The name of the database file.
        table_name (str): The name of the table to create or replace.
    """
    try:
        engine = create_engine(f'sqlite:///{database_name}') #create engine which is connection to specified db. sets configs for connection
        df.to_sql(table_name, con=engine, index=False, if_exists='replace') #create + write datafram to db. index = false because pandas adds index column i dont need that
        print(f"Data written to '{table_name}' table in '{database_name}' successfully.")
    except SQLAlchemyError as e:        
        print(f"Error: {e}")


def filter_non_explicit_songs():
    """
    Creates a new table (non_explict_songs) in spotify_stats.db with only non-explicit songs from spotify_statistics table
    """
    try:
        connection = sqlite3.connect('spotify_stats.db')
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS non_explicit_songs AS
            SELECT * FROM spotify_statistics WHERE explicit = 0""")
        connection.commit()
        print("Non-explicit songs table created successfully")
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        connection.close()
