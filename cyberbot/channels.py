# channels.py - functions for handling messages in server channels
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
from .utils import officers_only


async def handle_rule_accept_channel(message,role_name):
    if ((message.content.rstrip().upper() == "I ACCEPT") or 
        (message.content.rstrip().upper() == "I ACCEPT.") or 
        (message.content.rstrip().upper() == "I ACCEPT!")):
            role = discord.utils.get(client.guild.roles, name=role_name)
            if not role:
                print(f"[ERROR]: could not find role '{role_name}'!")
                return
            await message.author.add_roles(role)
            client.non_members.remove(message.author.id)
            print(f"Added {message.author.name} to role {role}")

@officers_only
async def handle_election_channel(message):
    if message.guild != client.guild: # security
        return
    slices = message.content.lower().split(' ',1)
    if slices[0] == "!get":
        if len(slices) > 1:
            ret = "An election is not currently in session."
            if slices[1] == "nominations":
                await message.channel.send(client.election.get_nominations() if client.election else ret)
                return
            elif slices[1] == "votes":
                await message.channel.send(client.election.get_votes() if client.election else ret)
                return
        await message.channel.send("unknown command")
    elif slices[0] == "!nomination":
        if len(slices) == 2:
            split_slices = slices[1].split(' ',1)
            ret = "A nomination is not currently in session."
            if split_slices[0] == "start":
                client.start_election_instance() # kick off election
                await message.channel.send("Setting up nomination data (this will take just a minute)...")
                ret = await client.election.start_nomination(split_slices[1].split(' ') if len(split_slices) > 1 else None)
                # end election instance if nomination start was executed incorrectly
                await message.channel.send(ret)
                if "Please specify" in ret or "No members" in ret:
                    client.end_election_instance()
            elif split_slices[0] == "stop":
                await message.channel.send(client.election.stop_nomination(split_slices[1] if len(split_slices) > 1 else None) if client.election else ret)
    elif slices[0] == "!election":
        if len(slices) > 1:
            ret = "An election cycle has not yet begun."
            if slices[1] == "start":
                await message.channel.send(client.election.start_election() if client.election else ret)
            elif slices[1] == "stop":
                await message.channel.send(client.election.stop_election() if client.election else ret)
                if ret != "An election cycle has not yet begun.":
                    client.end_election_instance()