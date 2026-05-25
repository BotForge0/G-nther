import os
import uuid
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from gtts import gTTS

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

voice_map = {
    "frau": "de",
    "mann": "de",
    "english": "en",
    "france": "fr"
}

active_tasks = {}

class VoiceSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Frau", value="frau", emoji="👩"),
            discord.SelectOption(label="Mann", value="mann", emoji="👨"),
            discord.SelectOption(label="English", value="english", emoji="🇺🇸"),
            discord.SelectOption(label="France", value="france", emoji="🇫🇷")
        ]

        super().__init__(
            placeholder="Stimme auswählen",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_voice = self.values[0]

        embed = discord.Embed(
            title="✅ Stimme gesetzt",
            description=f"Ausgewählt: `{self.values[0]}`",
            color=discord.Color.green()
        )

        await interaction.response.edit_message(embed=embed, view=self.view)

class VoiceView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.selected_voice = "frau"
        self.add_item(VoiceSelect())

async def create_tts(text, lang):
    file_name = f"{uuid.uuid4()}.mp3"

    tts = gTTS(
        text=text,
        lang=lang,
        slow=False
    )

    tts.save(file_name)

    return file_name

async def play_audio(vc, file_name):
    vc.play(discord.FFmpegPCMAudio(file_name))

    while vc.is_playing():
        await asyncio.sleep(1)

    os.remove(file_name)

async def broadcast_task(interaction, text, voice):
    guild_count = 0
    channel_count = 0
    user_count = 0

    lang = voice_map[voice]

    final_text = f"{text}. Powered by BotForge"

    for guild in bot.guilds:
        guild_count += 1

        for channel in guild.voice_channels:
            humans = [m for m in channel.members if not m.bot]

            if len(humans) == 0:
                continue

            try:
                vc = await channel.connect(timeout=10)

                file_name = await create_tts(final_text, lang)

                await play_audio(vc, file_name)

                user_count += len(humans)
                channel_count += 1

                await vc.disconnect(force=True)

                await asyncio.sleep(2)

            except:
                pass

    embed = discord.Embed(
        title="📢 Broadcast beendet",
        color=discord.Color.blurple()
    )

    embed.add_field(name="Server", value=f"`{guild_count}`")
    embed.add_field(name="Channels", value=f"`{channel_count}`")
    embed.add_field(name="Erreichte Nutzer", value=f"`{user_count}`")
    embed.add_field(name="Voice", value=f"`{voice}`", inline=False)

    await interaction.followup.send(embed=embed)

@bot.event
async def on_ready():
    await bot.tree.sync()

    print(f"{bot.user} gestartet")

@bot.tree.command(name="say", description="Voice Broadcast starten")
@app_commands.describe(
    text="Nachricht die gesagt werden soll"
)
async def say(interaction: discord.Interaction, text: str):
    view = VoiceView()

    embed = discord.Embed(
        title="🎤 Voice Broadcast",
        description="Wähle eine Stimme aus",
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(
        embed=embed,
        view=view,
        ephemeral=True
    )

    timeout = 0

    while timeout < 120:
        await asyncio.sleep(1)
        timeout += 1

        if view.selected_voice:
            break

    task = asyncio.create_task(
        broadcast_task(
            interaction,
            text,
            view.selected_voice
        )
    )

    active_tasks[interaction.user.id] = task

@bot.tree.command(name="stopbroadcast", description="Broadcast stoppen")
async def stopbroadcast(interaction: discord.Interaction):
    task = active_tasks.get(interaction.user.id)

    if not task:
        return await interaction.response.send_message(
            "❌ Kein aktiver Broadcast",
            ephemeral=True
        )

    task.cancel()

    del active_tasks[interaction.user.id]

    await interaction.response.send_message(
        "🛑 Broadcast gestoppt",
        ephemeral=True
    )

@bot.tree.command(name="ping", description="Bot Ping")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)

    embed = discord.Embed(
        title="🏓 Pong",
        description=f"`{latency}ms`",
        color=discord.Color.green()
    )

    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
