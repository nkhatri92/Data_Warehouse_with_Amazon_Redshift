# Data_Warehouse_with_Amazon_Redshift
Project 3 of the Udacity Nano Degree

In this project I created an ETL pipeline for a database hosted on Redshift. I loaded data from S3 to staging tables on Redshift and execute SQL statements that created the analytics tables from these staging tables. Finally, I tested the tables against some sample analytical queries handed by the analytics team as part of their requirements specification.

## Analytics Team's Requirement
A fictitious music streaming startup, Sparkify, has grown their user base and song database and want to move their processes and data onto the cloud. Their data resides in S3, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

The task is to build an ETL pipeline that extracts their data from S3, stages them in Redshift, and transforms data into a fact table and set of dimensional tables for their analytics team to continue finding insights in what songs their users are listening to.

I completed the task by creating ETL pipeline and tested it by running some sample analytical queries against the database.

## Data

Data set is a set of files in JSON format stored in AWS S3 buckets and contains two parts:
* **s3://udacity-dend/song_data**: static data about artists and songs
  Song-data example:
  `{"num_songs": 1, "artist_id": "ARJIE2Y1187B994AB7", "artist_latitude": null, "artist_longitude": null, "artist_location": "", "artist_name": "Line Renaud", "song_id": "SOUPIRU12A6D4FA1E1", "title": "Der Kleine Dompfaff", "duration": 152.92036, "year": 0}`

* **s3://udacity-dend/log_data**: event data of service usage e.g. who listened what song, when, where, and with which client
  ![Log-data example (log-data/2018/11/2018-11-12-events.json)](./Udacity-DEND-C3-Project3-LogDataExample-20190504.png)
* **s3://udacity-dend/log_json_path.json**: ...

Below, some figures about the data set (results after running the etl.py):

* s3://udacity-dend/song_data: 14897 files, 385252 DB rows
* s3://udacity-dend/log_data: 31 files, 8056 DB rows
* songplays: 245719 rows
* (unique) users: 104 rows
* songs: 384824 rows
* artists: 45266 rows
* time: 6813 rows

## Solution
### Database Schema
I decided to build database using following Star schema. In this schema, the *songplays* table serves as fact table containing information related to user's activity of listening to songs at specific times. Tables called *users, artists, time and songs* serve as dimension tables, which are referenced through foreign keys present in *songplays* fact table.

![](song_plays_database_ERD.png)

### ETL Pipeline
#### Data
* The data about events generated as part of user activity for e.g. listening next song, are stored as separate log files in JSON format in Amazon S3. This log files also contains information about user like first name, last name, location etc. They also contain information about the event like timestamp when user starts listening song, title of the song and its id, song's time length, artist name etc.
* The metadata about a large collection of songs is stored as files in JSON format in a separate directory on Amazon S3.

#### Loading into Redshift
I created two staging tables called *staging_events* and *staging_songs* to first load the data from JSON files in S3 into Redshift before doing further processing. I executed the COPY commands available in S3 that allows directly loading data of user activity log and songs in JSON format from S3 to database tables in Redshift Cluster. It's worth noting that thanks to this feature of directly importing data from S3 to Redshift Cluster, I didn't have to copy any data in local storage of the system where my ETL python script was executed.

    # This is how the queries with COPY commands for loading data from S3 to Redshift Cluster looks like  
    staging_events_copy = ("""
        COPY staging_events from {}
        iam_role {}
        json {}
        region 'us-west-2';
    """).format(config['S3']['LOG_DATA'], config["IAM_ROLE"]["ARN"], config['S3']['LOG_JSONPATH'])
    
    staging_songs_copy = ("""
        COPY staging_songs from {}    
        iam_role {}
        format as json 'auto'
        region 'us-west-2';    
    """).format(config['S3']['SONG_DATA'], config["IAM_ROLE"]["ARN"])

Then I ran different SQL INSERT queries by selecting data from staging tables to load it into facts table *songplays* and dimension tables like *users, artists and time*. Storing the data related to events like playing songs in separate table which contains foreign keys to dimension tables allows to run analytical queries while minimizing as data redundancy.

The dimension tables are designed to contain majority of the information related to the entity being represented by them and there by minimizing JOIN operations required to access information about any dimension while executing analytical queries.

### Organization of solution code in files
The code has been modularized into different files.
* `create_tables.py` is a python script useful for dropping existing tables and creating new ones of types staging, facts and dimensions in AWS Redshift cluster database.
* `etl.py` is a python script for performing ETL operation i.e. loading events and songs data from S3 into Redshift cluster and filling up staging, facts and dimensions tables. It also executes some sample analytical queries and prints the results.
* `sql_queries.py` contains all the declarations of the queries that are used by *create_tables.py* for creating and dropping tables and *etl.py* for copying data from S3 to staging using COPY commands and from staging tables to facts and dimensions tables using SQL INSERT queries. 
* `dwh.cfg` specifies configuration values for connecting to Redshift cluster database and locations of data files in S3.

### How to run the solution
The python scripts in this project are meant to be run by Python version 3+. Following commands are to be run after setting current directory of terminal to be project's directory.
The scripts assumes the Redshift cluster to be available and is accepting TCP connection on port 5439 from the machine on which the scripts will be executed. The configuration details related to Redshift cluster is stored in `dwh.cfg` file in project directory. One must specify details like Redshift cluster hostname, database name, username, password and database port. It also expects IAM Role that is to be assumed the database cluster to COPY data from S3. Finally the locations of files where the data about user activity logs and songs are stored and the path to file containing JSONpaths for converting log files from JSON to database entries has to be specified in `dwh.cfg`.

To create tables in Redshift, run following command in the terminal with current directory set to project's directory.

    python create_tables.py

To start ETL process of loading data from S3 to staging area, from staging area to facts and dimension tables and finally running some sample queries to test everything, run following command.

    python etl.py


