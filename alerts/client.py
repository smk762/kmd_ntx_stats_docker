#!/usr/bin/env python3.12
import time
import discord
import asyncio
from config import ALERT_INTERVAL, DISCORD_CHANNEL, DISCORD_TOKEN
from models import NotaryMonitor
from logger import logger

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sauron = NotaryMonitor()

    async def setup_hook(self) -> None:
        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.process_alerts())

    async def on_ready(self):
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info('------')

    async def process_alerts(self):
        await self.wait_until_ready()
        logger.info('Logged in as')
        logger.info(self.user.name)
        logger.info(self.user.id)
        logger.info('------')
        channel = self.get_channel(DISCORD_CHANNEL)
        while not self.is_closed():
            
            try:
                loop = 0
                while True:
                    msg = self.sauron.alert_slow_miners()
                    if msg != "":
                        # await self.channel.send(msg)
                        logger.info(msg)
                        break

                    if loop > 12:
                        await channel.send(f"<@448777271701143562> Mining endpoint not responding!\n")
                        break
                    time.sleep(60)
                    loop += 1

            except Exception as e:
                await channel.send(f"<@448777271701143562> Mining endpoint not responding!\n{e}")
            await asyncio.sleep(ALERT_INTERVAL)



if __name__ == '__main__':
    client = MyClient(intents=discord.Intents.default())
    client.run(DISCORD_TOKEN)
