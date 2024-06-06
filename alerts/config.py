import os
from dotenv import load_dotenv
load_dotenv()

ALERT_INTERVAL = 60*60*8 # 8 hours
try:
    DISCORD_CHANNEL = int(os.getenv('DISCORD_CHANNEL'))
except:
    print("You need to add 'DISCORD_CHANNEL' to .env file")

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
if DISCORD_TOKEN is None:
    print("You need to add 'DISCORD_TOKEN' to .env file")