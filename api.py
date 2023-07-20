###########################
# File: api.py
# Description: API for the BinDayBot discord bot
# Author: Jack Fitton
# Created: 20/07/2023
###########################

# Imports
import discord
import sqlite3
import datetime
import os
import requests
import asyncio


def init_db():

    # Connect to the database
    conn = sqlite3.connect('bindaybot.db')
    c = conn.cursor()

    # Create the users table
    # id - primary key integer
    # discord_id - integer
    # name - text
    # postcode - text
    # uprn - integer

    c.execute('''CREATE TABLE IF NOT EXISTS users
            (
              id INTEGER PRIMARY KEY,
              discord_id INTEGER,
              name TEXT,
              postcode TEXT,
              uprn INTEGER
              )''')
    
    conn.commit()
    conn.close()

def get_uprn_from_postcode(postcode: str) -> int or None:
        
        #strip the postcode of spaces
        postcode = postcode.replace(" ", "")
    
        # Get the uprn from the postcodes.io api
        url = "https://addresses.york.gov.uk/api/address/lookupbypostcode/" + postcode
        response = requests.get(url)

        # Check the response is valid
        if response.status_code == 200:
             return response.json()[0]['uprn']
        else:
            return None

def add_user(discord_id: int, name: str, postcode: str) -> bool:

    # Connect to the database
    conn = sqlite3.connect('bindaybot.db')
    c = conn.cursor()

    #get the uprn from the postcode and house number
    uprn = get_uprn_from_postcode(postcode)

    try:
    # Insert the user into the database
        c.execute("INSERT INTO users (discord_id, name, postcode, uprn) VALUES (?, ?, ?, ?)", (discord_id, name, postcode, uprn))
    except sqlite3.IntegrityError:
        return False
    

    conn.commit()
    conn.close()
    return True

def get_collection_data(uprn: int) -> list or None:
     
     # Get the collection data from the waste-api
    url = "https://waste-api.york.gov.uk/api/Collections/GetBinCollectionDataForUprn/" + str(uprn)
     
    response = requests.get(url)

    # Check the response is valid
    if response.status_code == 200:
         return response.json()
    else:
        return None
    
def get_next_collection_date(uprn: int) -> str or None:
     
     # Get the collection data from the waste-api
    url = "https://waste-api.york.gov.uk/api/Collections/GetBinCollectionDataForUprn/" + str(uprn)
     
    response = requests.get(url)

    # Check the response is valid
    if response.status_code != 200:
        return None
    
    # Get the next collection date
    collection_data = response.json()["services"]

    closest_date = None

    for collection in collection_data:
         
        next_collection = collection["nextCollection"]

        if next_collection is not None:
            collection_date = datetime.datetime.strptime(next_collection, '%Y-%m-%dT%H:%M:%S')
            if closest_date is None or collection_date < closest_date:
                closest_date = collection_date
    

    return closest_date.strftime("%d/%m/%Y")

def collection_tommorrow() -> list or None:

    #connect to the database
    conn = sqlite3.connect('bindaybot.db')
    c = conn.cursor()

    #get the current date
    today = datetime.datetime.now()

    #get the date for tommorrow
    tommorrow = today + datetime.timedelta(days=1)

    #go through all the users and get their collection data

    c.execute("SELECT * FROM users")

    users = c.fetchall()

    #close the database
    conn.close()

    #create a list of users who have a collection tommorrow
    users_with_collection = []

    for user in users:

        next_collection = get_next_collection_date(user[4])

        if next_collection is not None:
            if next_collection == tommorrow.strftime("%d/%m/%Y"):
                users_with_collection.append(user)

    return users_with_collection

def get_user_data(discord_id: int) -> list or None:

    # Connect to the database
    conn = sqlite3.connect('bindaybot.db')
    c = conn.cursor()

    # Get the user from the database
    c.execute("SELECT * FROM users WHERE discord_id = ?", (discord_id,))
    user = c.fetchone()

    # Close the database
    conn.close()

    return user

def get_user_collection_data(discord_id: int) -> list or None:
    
        # Connect to the database
        conn = sqlite3.connect('bindaybot.db')
        c = conn.cursor()
    
        # Get the user from the database
        c.execute("SELECT * FROM users WHERE discord_id = ?", (discord_id,))
        user = c.fetchone()
    
        # Close the database
        conn.close()
    
        uprn = user[4]

        return get_collection_data(uprn)



def pretty_send(collection_data: list):

    # format the collection data

    message = "Your next collections are:\n"

    for collection in collection_data["services"]:
        collection_date = collection["nextCollection"]
        collection_type = collection["binDescription"]
        collection_service = collection["service"]

        collection_date = datetime.datetime.strptime(collection_date, '%Y-%m-%dT%H:%M:%S')
        collection_date = collection_date.strftime("%d/%m/%Y")

        message += f"{collection_service} ({collection_type}) - {collection_date}\n"
           

    return message

def is_user(discord_id: int) -> bool:

    # Connect to the database
    conn = sqlite3.connect('bindaybot.db')
    c = conn.cursor()

    # Get the user from the database
    c.execute("SELECT * FROM users WHERE discord_id = ?", (discord_id,))

    user = c.fetchone()

    # Close the database
    conn.close()

    if user is None:
        return False
    else:
        return True


def main():

    # Initialise the database
    init_db()

