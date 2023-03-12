import obspython as obs
import os
import asyncio
import threading
import textwrap
import collections
from twitchio.ext import commands
from datetime import time
from dotenv import load_dotenv

# -------------------------------------------------------------
# Script settings
def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "token", "Your_Twitch_Bot_Token")
    obs.obs_data_set_default_string(settings, "prefix", "?")
    obs.obs_data_set_default_string(settings, "initial_channels", "initial_channels")
    obs.obs_data_set_default_string(settings, "Text Type Source", "Boot_Chat_Test")

def script_description():
    return "Updates a text source with chat messages from a Twitch bot."

def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "token", "Twitch Bot Token", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "prefix", "Twitch Bot Prefix", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "initial_channels", "Twitch Bot Initial Channels", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "Text Type Source", "Boot_Chat_Test", obs.OBS_TEXT_DEFAULT)

    return props

# -------------------------------------------------------------
# Twitch bot class




# -------------------------------------------------------------


class Bot(commands.Bot):

    def __init__(self,token, prefix, initial_channels):
        super().__init__(token=token, prefix=prefix, initial_channels=initial_channels)
        print('Bot started')
    
    async def event_ready(self):
        update_text(f'Logged in as | {self.nick}')
        print(f'Logged in as | {self.nick}')
        
    async def event_message(self, message):
        update_text(f"{message.author.name}: {message.content}")
        print(f"{message.author.name}: {message.content}")

    @commands.command()
    async def hello(self, ctx: commands.Context):
        await ctx.send(f'Hello {ctx.author.name}!')
    
    async def logout(self):
        await super().close()
        self.is_running = False


async def bot_run(settings):
    print("Starting bot...")
    global bot
    global source_name
    token = obs.obs_data_get_string(settings, "token")
    prefix = obs.obs_data_get_string(settings, "prefix")
    initial_channels = obs.obs_data_get_string(settings, "initial_channels")
    source_name = obs.obs_data_get_string(settings, "Text Type Source")
    bot = Bot(token=token, prefix=prefix, initial_channels=[initial_channels])
    await bot.start()

async def stop_halt():
    global bot
    print("Stopping bot...")
    if bot:
        await bot.logout()
        bot = None



def start_bot(settings):
    global bot_thread
    bot_thread = threading.Thread(target=asyncio.run, args=(bot_run(settings),), name='BotThread')
    bot_thread.start()

def stop_bot():
    global bot_thread
    global bot
    bot.loop.create_task(bot.logout())




# -------------------------------------------------------------

def pad_string(s, desired_length):
    return s.ljust(desired_length)


chunks_fifo = collections.deque(maxlen=30)

def update_text(text_fronm_chatbot):
    chunk_size = 30
    global chunks_fifo
    global chunks
    chunks = []

    if text_fronm_chatbot:
        chunks = textwrap.wrap(text_fronm_chatbot, chunk_size)
        for i , chunk in enumerate(chunks):
            if len(chunk) < 30:
                chunks_fifo.append(chunk + " " * (chunk_size - len(chunk)))
            else:
                chunks_fifo.append(chunk)

    print(f"{chunks_fifo}")
    chunks_fifo_text= "\n".join(chunks_fifo)
    
    source = obs.obs_get_source_by_name(source_name)
    if source is not None:
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "text", chunks_fifo_text)
        obs.obs_source_update(source, settings)
        obs.obs_data_release(settings)
        obs.obs_source_release(source)


def script_load(settings):
    start_bot(settings)


def script_unload():
    stop_bot()

# ------------------------------------------------------------


def script_description():
    return "Updates a text source to the curent date and time"
