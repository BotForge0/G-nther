import discord
from discord.ext import commands
from discord import app_commands
from gtts import gTTS
import asyncio
import os

TOKEN = "MTUwODYwNjUxMTY3OTU0MTI0OQ.GlFwI7.yZ_GdGL7psfJUkcVPqxZZmNVuz-CLfoT-poACE"

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

voices = {
    "mann": "de",
    "frau": "de"
}

async def play_tts(vc, text, lang):
    file_name = "tts.mp3"

    tts = gTTS(text=text, lang=lang)
    tts.save(file_name)

    vc.play(discord.FFmpegPCMAudio(file_name))

    while vc.is_playing():
        await asyncio.sleep(1)

    os.remove(file_name)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} online")

@bot.tree.command(name="say", description="Bot spricht in Voice Channels")
@app_commands.describe(
    text="Was gesagt werden soll",
    voice="Sprachart"
)
@app_commands.choices(voice=[
    app_commands.Choice(name="Mann", value="mann"),
    app_commands.Choice(name="Frau", value="frau")
])
async def say(
    interaction: discord.Interaction,
    text: str,
    voice: app_commands.Choice[str] = None
):
    await interaction.response.send_message("Starte Voice Broadcast...", ephemeral=True)

    selected_voice = "frau"

    if voice:
        selected_voice = voice.value

    lang = voices[selected_voice]

    final_text = f"{text}. Powered by BotForge"

    for guild in bot.guilds:
        for channel in guild.voice_channels:

            humans = [m for m in channel.members if not m.bot]

            if len(humans) > 0:
                try:
                    vc = await channel.connect()

                    await play_tts(vc, final_text, lang)

                    await asyncio.sleep(1)

                    await vc.disconnect()

                    await asyncio.sleep(2)

                except Exception as e:
                    print(e)

bot.run(TOKEN)
