import discord
from discord.ext import commands
import asyncio
from gtts import gTTS
import os

TOKEN = ""

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

TEXT = "Hallo, das ist eine automatische Nachricht. Poweredby BotForge"

async def play_tts(vc, text):
    tts = gTTS(text=text, lang="de")
    tts.save("tts.mp3")

    vc.play(discord.FFmpegPCMAudio("tts.mp3"))

    while vc.is_playing():
        await asyncio.sleep(1)

    os.remove("tts.mp3")

@bot.command()
async def voice(ctx):
    for guild in bot.guilds:
        for channel in guild.voice_channels:
            humans = [m for m in channel.members if not m.bot]

            if len(humans) > 0:
                try:
                    vc = await channel.connect()

                    await play_tts(vc, TEXT)

                    await asyncio.sleep(1)

                    await vc.disconnect()

                    await asyncio.sleep(2)

                except Exception as e:
                    print(e)

bot.run(TOKEN)
