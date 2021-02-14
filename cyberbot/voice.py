# voice.py - functions dealing with voice channel management
# 
# This file is part of CyberBot.
# 
# CyberBot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# CyberBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with CyberBot.  If not, see <https://www.gnu.org/licenses/>.
#

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