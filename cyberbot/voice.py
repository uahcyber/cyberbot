import discord
from .run import client

def members_in_voice_channel(channel):
    if isinstance(channel,discord.VoiceChannel):
        return channel.members

def is_member_in_voice_channel(member,channel_name):
    vc = discord.utils.get(client.guild.channels,name=channel_name)
    if vc:
        if member in members_in_voice_channel(vc):
            return True
    return False