import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events "
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplay"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS song"
artist_table_drop = "DROP TABLE IF EXISTS artist"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES
staging_events_table_create= ("""CREATE TABLE IF NOT EXISTS staging_events(
    artist         varchar,
    auth           varchar,
    firstname      varchar,
    gender         varchar,
    iteminsession  int ,
    lastname       varchar,
    length         numeric,
    level          varchar, 
    location       varchar,
    method         varchar,
    page           varchar,
    registration   numeric,
    sessionid      int,
    song           varchar,
    status         int,
    ts             bigint,
    useragent      varchar,
    userid         int) 
""")


staging_songs_table_create = ("""CREATE TABLE IF NOT EXISTS staging_songs(
    num_songs           int, 
    artist_id           varchar, 
    latitude            numeric, 
    longitude           numeric,
    location            varchar,
    artist_name         varchar,
    song_id             varchar,
    title               varchar,
    duration            numeric,
    year                int) 
""")

songplay_table_create = ("""CREATE TABLE IF NOT EXISTS songplay(
    songplay_id              int IDENTITY(0,1) PRIMARY KEY, 
    start_time               timestamp NOT NULL, 
    user_id                  int NOT NULL, 
    level                    varchar, 
    song_id                  varchar, 
    artist_id                varchar, 
    session_id               int, 
    location                 varchar, 
    user_agent               varchar
)
""")

user_table_create = ("""CREATE TABLE IF NOT EXISTS users(
    user_id                 int NOT NULL PRIMARY KEY, 
    first_name              varchar,
    last_name               varchar, 
    gender                  varchar,
    level                   varchar
    )
""")

song_table_create = ("""CREATE TABLE IF NOT EXISTS song(
    song_id                  varchar NOT NULL PRIMARY KEY,
    title                    varchar, 
    artist_id                varchar, 
    year                     int, 
    duration                 numeric
)
""")

artist_table_create = ("""CREATE TABLE IF NOT EXISTS artist(
    artist_id                varchar NOT NULL PRIMARY KEY,
    artist_name              varchar, 
    location                 varchar,
    latitude                 numeric, 
    longitude                numeric

)
""")

time_table_create = ("""CREATE TABLE IF NOT EXISTS time(
    start_time               timestamp NOT NULL PRIMARY KEY, 
    hour                     int NOT NULL , 
    day                      int NOT NULL, 
    week                     int NOT NULL, 
    month                    varchar NOT NULL, 
    year                     int NOT NULL, 
    weekday                  varchar NOT NULL

) 
""")


# STAGING TABLES

staging_events_copy = ("""
copy staging_events
from {}
iam_role {}
json {}
""").format(config['S3']['LOG_DATA'], config["IAM_ROLE"]["ARN"], config['S3']['LOG_JSONPATH'])

staging_songs_copy=("""
copy staging_songs 
from {} 
iam_role {}
json 'auto'
""").format(config['S3']['SONG_DATA'], config["IAM_ROLE"]["ARN"])

# FINAL TABLES

songplay_table_insert = (""" INSERT INTO songplay (
        start_time,
        user_id,
        level,
        song_id,
        artist_id,
        session_id,
        location,
        user_agent) 
    SELECT 
        se.start_time,
        se.userid, 
        se.level,
        ss.song_id, 
        ss.artist_id,
        se.sessionid, 
        se.location, 
        se.useragent
    FROM (SELECT timestamp 'epoch' + ts/1000 * interval '1 second' AS start_time, *FROM staging_events WHERE page = 'NextSong') se LEFT JOIN staging_songs ss ON (se.song = ss.title AND se.length=ss.duration AND se.artist = ss.artist_name)
""")

user_table_insert = (""" INSERT INTO users (
        user_id,
        first_name, 
        last_name,
        gender, 
        level) SELECT userid, firstname, lastname, gender, level FROM staging_events WHERE page = 'NextSong'
""")

song_table_insert = (""" INSERT INTO song (
        song_id, 
        title, 
        artist_id, 
        year,
        duration) 
        
SELECT
        song_id, 
        title, 
        artist_id, 
        year,
        duration 
        
FROM staging_songs;
""") 

artist_table_insert = (""" INSERT INTO artist (
        artist_id,
        artist_name,
        location,
        latitude,
        longitude
    )
        
    SELECT 
        artist_id,
        artist_name,
        location,
        latitude,
        longitude
        
    FROM staging_songs
""")

time_table_insert = (""" INSERT INTO time (
        start_time,
        hour,
        day,
        week,
        month,
        year,
        weekday)
        
    SELECT 
        start_time,                               
        EXTRACT(hour from start_time),
        EXTRACT(day from start_time),
        EXTRACT(week from start_time),
        EXTRACT(month from start_time),
        EXTRACT(year from start_time),
        EXTRACT(weekday from start_time)
            
    FROM 
        songplay;
        
""")



# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
