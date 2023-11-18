# importing the necessary libraries
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_option_menu import option_menu
import mysql.connector as sql
import pymongo
from googleapiclient.discovery import build
from PIL import Image
import re
from datetime import datetime

# SETTING PAGE CONFIGURATIONS
icon = Image.open("Youtube_logo.png")
st.set_page_config(page_title="Youtube DataHarvesting and Warehousing",
                   page_icon=icon,
                   layout="wide",
                   initial_sidebar_state="expanded",
                   menu_items={'About': """# This app is created by *Aarif*"""})

# CREATING OPTION MENU
with st.sidebar:
    selected = option_menu(None, ["Home", "Extract and Transform", "View"],
                           icons=["house-door-fill", "tools", "card-text"],
                           default_index=0,
                           orientation="vertical",
                           styles={"nav-link": {"font-size": "30px", "text-align": "centre", "margin": "0px",
                                                "--hover-color": "#C80101"},
                                   "icon": {"font-size": "30px"},
                                   "container": {"max-width": "6000px"},
                                   "nav-link-selected": {"background-color": "#C80101"}})

# Bridging a connection with MongoDB Atlas and Creating a new database(youtube_data)
client = pymongo.MongoClient("mongodb+srv://mdarif16521:Guvi1234@cluster0.z8bssuf.mongodb.net/")
db = client['youtube_data']

# CONNECTING WITH MYSQL DATABASE
mydb = sql.connect(host="localhost",
                   user="root",
                   password="Guvi1234",
                   database="youtube_db"
                   )
mycursor = mydb.cursor(buffered=True)

# BUILDING CONNECTION WITH YOUTUBE API
api_key = "AIzaSyCkglXpsoXo7QjsLDBAL8mzCfX4YZzpdtg"
youtube = build('youtube', 'v3', developerKey=api_key)


# FUNCTION TO GET CHANNEL DETAILS
def get_channel_details(channel_id):
    ch_data = []
    response = youtube.channels().list(part='snippet,contentDetails,statistics',
                                       id=channel_id).execute()

    for i in range(len(response['items'])):
        data = dict(Channel_id=channel_id[i],
                    Channel_name=response['items'][i]['snippet']['title'],
                    Playlist_id=response['items'][i]['contentDetails']['relatedPlaylists']['uploads'],
                    Subscribers=response['items'][i]['statistics']['subscriberCount'],
                    Views=response['items'][i]['statistics']['viewCount'],
                    Total_videos=response['items'][i]['statistics']['videoCount'],
                    Description=response['items'][i]['snippet']['description'],
                    Country=response['items'][i]['snippet'].get('country')
                    )
        ch_data.append(data)
    return ch_data


# FUNCTION TO GET VIDEO IDS
def get_channel_videos(channel_id):
    video_ids = []
    # get Uploads playlist id
    res = youtube.channels().list(id=channel_id,
                                  part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    next_page_token = None

    while True:
        res = youtube.playlistItems().list(playlistId=playlist_id,
                                           part='snippet',
                                           maxResults=50,
                                           pageToken=next_page_token).execute()

        for i in range(len(res['items'])):
            video_ids.append(res['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token = res.get('nextPageToken')

        if next_page_token is None:
            break
    return video_ids


# FUNCTION TO GET VIDEO DETAILS
def get_video_details(v_ids):
    video_stats = []

    for i in range(0, len(v_ids), 50):
        response = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=','.join(v_ids[i:i + 50])).execute()
        for video in response['items']:
            video_details = dict(Channel_name=video['snippet']['channelTitle'],
                                 Channel_id=video['snippet']['channelId'],
                                 Video_id=video['id'],
                                 Title=video['snippet']['title'],
                                 Tags=video['snippet'].get('tags'),
                                 Thumbnail=video['snippet']['thumbnails']['default']['url'],
                                 Description=video['snippet']['description'],
                                 Published_date=video['snippet']['publishedAt'],
                                 Duration=video['contentDetails']['duration'],
                                 Views=video['statistics']['viewCount'],
                                 Likes=video['statistics'].get('likeCount'),
                                 Comments=video['statistics'].get('commentCount'),
                                 Favorite_count=video['statistics']['favoriteCount'],
                                 Definition=video['contentDetails']['definition'],
                                 Caption_status=video['contentDetails']['caption']
                                 )
            video_stats.append(video_details)
    return video_stats


# FUNCTION TO GET COMMENT DETAILS
def get_comments_details(v_id):
    comment_data = []
    try:
        next_page_token = None
        while True:
            response = youtube.commentThreads().list(part="snippet,replies",
                                                     videoId=v_id,
                                                     maxResults=100,
                                                     pageToken=next_page_token).execute()
            for cmt in response['items']:
                data = dict(Comment_id=cmt['id'],
                            Video_id=cmt['snippet']['videoId'],
                            Comment_text=cmt['snippet']['topLevelComment']['snippet']['textDisplay'],
                            Comment_author=cmt['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                            Comment_posted_date=cmt['snippet']['topLevelComment']['snippet']['publishedAt'],
                            Like_count=cmt['snippet']['topLevelComment']['snippet']['likeCount'],
                            Reply_count=cmt['snippet']['totalReplyCount']
                            )
                comment_data.append(data)
            next_page_token = response.get('nextPageToken')
            if next_page_token is None:
                break
    except:
        pass
    return comment_data


# FUNCTION TO GET CHANNEL NAMES FROM MONGODB
def channel_names():
    ch_name = []
    for i in db.channel_details.find():
        ch_name.append(i['Channel_name'])
    return ch_name
    
# Extracting minutes and seconds from the duration string
def durationtoint(duration_str):
   
    minutes = 0
    seconds = 0
    
    match = re.search(r"PT(\d+)M(\d+)S", duration_str)
    match1 = re.search(r"PT(\d+)M", duration_str)
    match2 = re.search(r"PT(\d+)S", duration_str)
    
    if match:
        minutes_str = match.group(1)
        seconds_str = match.group(2)
        minutes = int(minutes_str)
        seconds = int(seconds_str)
        total_seconds = minutes * 60 + seconds
        
    if match1:
        minutes_str = match1.group(1)
        minutes = int(minutes_str)
        total_seconds = minutes * 60 
       
    if match2:
        seconds_str = match2.group(1)
        seconds = int(seconds_str)
        total_seconds = seconds
            
    return total_seconds
    
# Remove Records from MySQL
def delsqlrec():
        option = st.selectbox("Select Delete option ⬇️", ["Delete single Channel Records", 'Delete Entire Channels Records'])
        if option == "Delete single Channel Records":
            mycursor.execute("select channel_name from channels")
            sqlchanname = [i[0] for i in mycursor.fetchall()]
            if len(sqlchanname)>0:
                sqloption = st.selectbox("Select Channel ⬇️", sqlchanname)
                if st.button("Proceed"):
                    # Getting correspoding channel id
                    mycursor.execute(f"select channel_id from channels where channel_name = '{sqloption}' ")
                    sqlchanid = mycursor.fetchall()
                    sqlchanid = sqlchanid[0][0]

                    # delete comment part query
                    mycursor.execute(f"delete from comments where video_id in (select video_id from videos where playlist_id = '{sqlchanid}')")
                    mydb.commit()

                    mycursor.execute(f"delete from videos where playlist_id in (select playlist_id from channels where  channel_id = '{sqlchanid}' )")
                    mydb.commit()

                    mycursor.execute(f"delete from playlists where playlist_id in (select playlist_id from channels where channel_id = '{sqlchanid}')")
                    mydb.commit()

                    mycursor.execute(f"delete from channels where channel_id ='{sqlchanid}' ")
                    mydb.commit()

                    st.success(f"The {sqloption} channel records has got deleted successfully",icon='✅')

                    mycursor.execute("select count(*) from channels")
                    res = mycursor.fetchall()
                    st.info(f"Total Channel Records :{res[0][0]}")
            else:
                st.error("No Channel Data Exists 🚫")

        elif option == 'Delete Entire Channels Records':

            mycursor.execute("select count(*) from channels")
            res = mycursor.fetchall()
            if res[0][0] > 0:
                    st.warning("Alert Confirm To Delete All Records ⚠️")
                    choose = st.selectbox("Choose ⬇️", ["Retain", "Drop All Records"])
                    if st.button("Proceed"):
                        if choose == "Retain":
                            st.success("Documents Retained", icon='✅')
                            # kept
                            mycursor.execute("select count(*) from channels")
                            res = mycursor.fetchall()
                            st.info(f"Total Documents :{res[0][0]}")

                        elif choose == "Drop All Records":
                            # Delete All Records in 4 Table
                            mycursor.execute("delete from channels")
                            mycursor.execute("delete from comments")
                            mycursor.execute("delete from videos")
                            mycursor.execute("delete from playlists")
                            mydb.commit()
                            mycursor.execute("select count(*) from channels")
                            res = mycursor.fetchall()
                            st.success("All Channel Data Successfully Deleted", icon='✅')
                            st.info(f"Total Channel Data :{res[0][0]}")

            else:
                st.error("No Channel Data Exists 🚫")
# HOME PAGE
if selected == "Home":
    # Title Image

    col1 = st.columns(1, gap='medium')
    col1[0].image("youtubeMain.png")
    col1[0].markdown("## :blue[Domain] : Social Media")
    col1[0].markdown("## :blue[Technologies used] : Python,MongoDB, Youtube Data API, MySql, Streamlit")
    col1[0].markdown(
        "## :blue[Overview] : Retrieving the Youtube channels data from the Google API, storing it in a MongoDB as data lake, migrating and transforming data into a SQL database,then querying the data and displaying it in the Streamlit app.")
    #col2.markdown("#   ")
    #col2.markdown("#   ")
    #col2.markdown("#   ")
    #col1.image("youtubeMain.png")

# EXTRACT and TRANSFORM PAGE
if selected == "Extract and Transform":
    tab1, tab2, tab3 = st.tabs(["$\huge EXTRACT $", "$\huge TRANSFORM $", "$\huge CLEAR $"])

    # EXTRACT TAB
    with tab1:
        st.markdown("#    ")
        st.write("### Enter YouTube Channel_ID below :")
        ch_id = st.text_input(
            "Hint : Goto channel's home page > Right click > View page source > Find channel_id").split(',')

        if ch_id and st.button("Extract Data"):
            ch_details = get_channel_details(ch_id)
            st.write(f'#### Extracted data from :green["{ch_details[0]["Channel_name"]}"] channel')
            st.table(ch_details)

        if st.button("Upload to MongoDB"):
            with st.spinner('Please Wait for it...'):
                ch_details = get_channel_details(ch_id)
                v_ids = get_channel_videos(ch_id)
                vid_details = get_video_details(v_ids)


                def comments():
                    com_d = []
                    for i in v_ids:
                        com_d += get_comments_details(i)
                    return com_d


                comm_details = comments()

                collections1 = db.channel_details
                collections1.insert_many(ch_details)

                collections2 = db.video_details
                collections2.insert_many(vid_details)

                collections3 = db.comments_details
                collections3.insert_many(comm_details)
                st.success("Upload to MogoDB successful !!")

    # TRANSFORM TAB
    with tab2:
        st.markdown("#   ")
        st.markdown("### Select a channel to begin Transformation to SQL")

        ch_names = channel_names()
        user_inp = st.selectbox("Select channel", options=ch_names)


        def insert_into_channels():
            collections = db.channel_details
          
# Migrate the data from MongoDB to MySQL

            for document in collections.find({"Channel_name": user_inp}, {'_id': 0}):
                query_insert_data = """INSERT INTO channels (channel_id,
                    channel_name,
                    channel_views,
                    channel_description
                    ) VALUES ( %s,%s, %s, %s);
                """
                values_insert_data = (
                    document['Channel_id'],
                    document['Channel_name'],
                    document['Views'],
                    document['Description']
                    )
                query_playlist = """
                    INSERT INTO playlists (
                        playlist_id,
                        channel_id,
                        channel_name
                        ) VALUES (%s, %s, %s)
                        """
                values_playlist = (
                    document['Playlist_id'],
                    document['Channel_id'],
                    document['Channel_name']
                    )
                mycursor.execute(query_insert_data, values_insert_data)
                mycursor.execute(query_playlist, values_playlist)
    # Commit the changes to the MySQL database
                mydb.commit()

        def insert_into_videos():
            collections = db.channel_details
            collectionss = db.video_details
# Migrate the data from MongoDB to MySQL
        #for document in collections.find({"Channel_name": user_inp}, {'_id': 0}):
            for video_data in collectionss.find({"Channel_name": user_inp}, {'_id': 0}):
                        published_date = datetime.strptime(video_data['Published_date'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")
                
                        query_video = """
                            INSERT INTO videos (
                            video_id,
                            playlist_id,
                            video_name,
                            video_description,
                            published_date,
                            view_count,
                            like_count,
                            comment_count,
                            duration,
                            thumbnail
                                ) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                            """
                        values_video = (
                                     video_data['Video_id'],
                                     video_data['Channel_id'],
                                     video_data['Title'],
                                     video_data['Description'],
                                     published_date,
                                     video_data['Views'],
                                     video_data['Likes'],
                                     video_data['Comments'],
                                     durationtoint(video_data['Duration']),
                                     video_data['Thumbnail']
                                    )
                    
                        mycursor.execute(query_video, values_video)
                # Commit the changes to the MySQL database
                        mydb.commit()
                   
                     
    


        def insert_into_comments():
            collections1 = db.video_details
            collections2 = db.comments_details
            
# Migrate the data from MongoDB to MySQL        
            for vid in collections1.find({"Channel_name": user_inp}, {'_id': 0}):
                for video_data in collections2.find({'Video_id': vid['Video_id']},{'_id' : 0}):
                    query_Comment = """
                        INSERT INTO comments (
                            comment_id,
                            video_id,
                            comment_text,
                            comment_author,
                            comment_published_date
                            )VALUES(%s,%s,%s,%s,%s)       
                                    """
                    #for i in range(len(video_data['Comments'])):
                    values_comment = (
                            video_data['Comment_id'],
                            video_data['Video_id'],
                            video_data['Comment_text'],
                            video_data['Comment_author'],
                            video_data['Comment_posted_date']
                        )
                    mycursor.execute(query_Comment, values_comment)
                    
                    mydb.commit()


        if st.button("Submit"):
            try:

                insert_into_channels()
                insert_into_videos()
                insert_into_comments()
                st.success("Transformation to MySQL Successful!!!")
            except:
                st.error("Channel details already transformed!!")
# CLEAR TAB
    with tab3:
        st.markdown("#   ")
        st.markdown("### Select a channel to Remove data from SQL")
        st.title(':red[DROP] RECORDS')
        delsqlrec()
        
# VIEW PAGE
if selected == "View":

    st.write("## :orange[Select any question to get Insights]")
    questions = st.selectbox('Questions',
                             ['Click the question that you would like to query',
                              '1. What are the names of all the videos and their corresponding channels?',
                              '2. Which channels have the most number of videos and how many videos do they have?',
                              '3. What are the top 10 most viewed videos and their respective channels?',
                              '4. How many comments were made on each video, and what are their corresponding video names?',
                              '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
                              '6. What is the total number of likes for each video, and what are their corresponding video names?',
                              '7. What is the total number of views for each channel, and what are their corresponding channel names?',
                              '8. What are the names of all the channels that have published videos before the year 2023?',
                              '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
                              '10. Which videos have the highest number of comments, and what are their corresponding channel names?'])

    if questions == '1. What are the names of all the videos and their corresponding channels?':
        mycursor.execute(
            """SELECT p.channel_name, v.video_name FROM playlists p JOIN videos v ON v.playlist_id = p.channel_id""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

    elif questions == '2. Which channels have the most number of videos and how many videos do they have?':
        mycursor.execute("""SELECT p.channel_name, COUNT(v.video_id) AS video_count FROM playlists p JOIN Videos v ON p.channel_id = v.playlist_id GROUP BY p.channel_name ORDER BY video_count DESC""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Number of videos in each channel :]")
        st.bar_chart(df,x= mycursor.column_names[0],y= mycursor.column_names[1])
        
        

    elif questions == '3. What are the top 10 most viewed videos and their respective channels?':
        mycursor.execute("""SELECT v.video_name, p.channel_name, v.view_count FROM videos v JOIN playlists p ON v.playlist_id = p.channel_id ORDER BY v.view_count DESC LIMIT 10""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Top 10 most viewed videos :]")
        fig = px.bar(df, x=mycursor.column_names[1], y=mycursor.column_names[2], color=mycursor.column_names[0])
        st.plotly_chart(fig)

    elif questions == '4. How many comments were made on each video, and what are their corresponding video names?':
        mycursor.execute("""SELECT Video_name, comment_count from videos ORDER BY comment_count DESC""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

    elif questions == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
        mycursor.execute("""SELECT v.video_name, p.channel_name, v.like_count FROM videos v JOIN playlists p ON v.playlist_id = p.channel_id ORDER BY v.like_count DESC LIMIT 10""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Top 10 most liked videos :]")
        

    elif questions == '6. What is the total number of likes for each video, and what are their corresponding video names?':
        mycursor.execute("""SELECT video_name, like_count FROM videos ORDER BY like_count DESC""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

    elif questions == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name, channel_views FROM channels ORDER BY channel_views""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write("### :green[Channels vs Views :]")
        st.write(df)
        
        fig = px.bar(df, x=mycursor.column_names[0], y=mycursor.column_names[1],color= mycursor.column_names[0])
        st.plotly_chart(fig)

    elif questions == '8. What are the names of all the channels that have published videos before the year 2023?':
        mycursor.execute("""SELECT p.channel_name, v.video_name, v.published_date FROM playlists p JOIN videos v ON p.channel_id = v.playlist_id WHERE EXTRACT(YEAR FROM v.published_date) < 2023 order by v.published_date""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

    elif questions == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        mycursor.execute("""SELECT p.channel_name,AVG(v.duration) AS Average_duration FROM playlists p JOIN videos v ON p.channel_id = v.playlist_id GROUP BY p.channel_name;""")
        st.write("### :green[Average video duration for channels :]")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)
        

    elif questions == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
        mycursor.execute("""SELECT p.channel_name, v.video_name, v.comment_count FROM playlists p JOIN videos v ON p.channel_id = v.playlist_id  ORDER BY comment_count DESC LIMIT 10""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write("### :green[Videos with most comments :]")
        st.write(df)
        
        #st.bar_chart(df,x= mycursor.column_names[0],y= mycursor.column_names[1])

