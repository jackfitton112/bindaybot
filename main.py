import api
import discord
from dotenv import load_dotenv
import os

load_dotenv()

api.main()

if os.getenv("DISCORD_TOKEN") is None:
    print("Please set the DISCORD_TOKEN environment variable")
    exit(1)

intents = discord.Intents.all()


client = discord.Client(intents=intents)

async def help(message):
    help_message = """```!setup <Postcode>``` - Setup your discord account to receive bin collection reminders"""
    await message.channel.send(help_message)

async def setup(message, postcode: str) -> None:
    if api.add_user(message.author.id, message.author.name, postcode):
        await message.channel.send("You have been added to the database")
    else:
        await message.channel.send("You are already in the database")

async def send_message(messagectx, message: str):
    await messagectx.channel.send(message)
    return


@client.event
async def on_ready():
    print("Bot is ready")

@client.event
async def on_message(message):

    print(f"{message.author} sent {message.content} in {message.guild}")
    if message.author == client.user:
        return
    
    if message.content.startswith("!help"):
        await help(message)
    
    elif message.content.startswith("!setup"):

        #check postcode is valid
        # !setup YO10 5DD
        #anything after first space is postcode

        postcode = message.content.replace("!setup ", "")

        #strip the postcode of spaces
        postcode = postcode.replace(" ", "")

        #check postcode is a string of 6-8 characters
        if len(postcode) >= 6 and len(postcode) <= 8:
            
            await setup(message, message.content.split(" ")[1])
            await message.channel.send("You have been added to the database")
        
        else:
            await message.channel.send("Invalid postcode format  - please use the format `!setup YO10 5DD`")

    elif message.content.startswith("!when"):

        if api.is_user(message.author.id):
            data = api.get_user_collection_data(message.author.id)
            if data is None:
                await message.channel.send("You are not in the database")
            else:
                await send_message(message, api.pretty_send(data))
        else:
            await message.channel.send("You are not in the database")


client.run(os.getenv("DISCORD_TOKEN"))
