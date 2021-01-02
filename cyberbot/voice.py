import discord
from .run import client

def members_in_voice_channel(channel):
    if isinstance(channel,discord.VoiceChannel):
        return channel.members