import os
from logger import logger
from dotenv import load_dotenv
load_dotenv()

ALERT_INTERVAL = 60*60*8 # 8 hours
try:
    DISCORD_CHANNEL = int(os.getenv('DISCORD_CHANNEL'))
except:
    logger.info("You need to add 'DISCORD_CHANNEL' to .env file")

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
if DISCORD_TOKEN is None:
    logger.info("You need to add 'DISCORD_TOKEN' to .env file")