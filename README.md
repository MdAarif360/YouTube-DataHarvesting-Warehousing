# YouTube Data Harvesting Warehousing


# Overview

      This project is focused on harvesting data from YouTube channels using the YouTube API, processing the data, and warehousing it. The harvested data is initially stored in a MongoDB Atlas database as documents and is then converted into SQL records for in-depth data analysis. The project's core functionality relies on the Extract, Transform, Load (ETL) process.
      Features

# Approach 
    Harvest YouTube channel data using the YouTube API by providing a 'Channel ID'.
    Store channel data in MongoDB Atlas.
    Convert MongoDB data into SQL records for data analysis.
    Use 11 different functions class to perform various tasks.
    Implement Streamlit to present code and data in a user-friendly GUI.
    Execute data analysis using SQL queries.

# Getting Started

    Install/Import the necessary modules: Streamlit, Pandas, PyMongo, MysqlConnector,Googleapiclient.
    Ensure you have access to MongoDB Atlas and set up a MySQL DBMS on your local environment.

# Technical Steps to Execute the Project

### Step 1: Install/Import Modules

    Ensure the required Python modules are installed: Streamlit, Pandas, PyMongo, MysqlConnector, Googleapiclient, and Isodate.

### Step 2: Utilization of functions

    There are 11 Functions, each with specific functionality for data extraction and transformation. These functions cover tasks like data retrieval, data storage, and data analysis.

### Step 3: Run the Project with Streamlit

    Open the command prompt in the directory where "app.py" is located.
    Execute the command: streamlit run app.py. This will open a web browser, such as Google Chrome, displaying the project's user interface.

### Step 4: Configure Databases

    Ensure that you are connected to both MongoDB Atlas and your local MySQL DBMS.

### Functions

    Get YouTube Channel Data: Fetches YouTube channel data using a Channel ID and creates channel details in JSON format.
    Get Playlist Videos: Retrieves all video IDs for a provided playlist ID.
    Get Video and Comment Details: Returns video and comment details for the given video IDs.
    Get All Channel Details: Provides channel, video, and playlist details in JSON format.
    Insert Data into MongoDB: Inserts channel data into MongoDB Atlas as a document.
    Get Channel Names from MongoDB: Retrieves channel names from MongoDB documents.
    Data Load to SQL: Loads data into SQL.
	Convert Duration: Convert the videos duration format into numbers
    Data Analysis: Conducts data analysis using SQL queries.
    Delete SQL Records: Deletes SQL records related to the provided YouTube channel data with various options.

# Skills Covered

    Python (Scripting)
    Data Collection
    MongoDB
    SQL
    API Integration
    Data Management using MongoDB (Atlas) and MySQL
    IDE: PyCharm Community Version
