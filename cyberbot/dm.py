# dm.py - functions for dealing with direct messages to the bot
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

import arrow
import discord
import os
from .run import client
from .voice import is_member_in_voice_channel
from .utils import make_file, officers_only, send_dm, parse_username_and_friend

async def handle_dm(user, msg=None):
    tosend = "beep beep boop boop, whatcha doin?"
    pieces = msg.rstrip().split(' ',1)
    async with user.typing():
        # check that user is a member of the current guild
        user = discord.utils.get(client.guild.members,name=user.name, discriminator=user.discriminator)
        user_roles = [role.name for role in user.roles]
        if "Member" not in user_roles:
            tosend = f"It does not seem like you are a member of the {client.clubname} server."
            return tosend
        if pieces[0] == "!nominate":
            if client.election and client.election.nomination_started:
                if not is_member_in_voice_channel(user,"meetings"): # must be present to vote/nominate
                    return
                if user.id in client.election.users_waiting_for_nom:
                    return # make sure a user waiting for a response cannot nominate someone during the wait
                if pieces[1] in ('accept', 'reject','cancel','second'):
                    return
                tosend = await client.election.handle_nominate(user,pieces[1]) or tosend
        elif pieces[0] == "!vote":
            if client.election and client.election.election_started:
                if not is_member_in_voice_channel(user,"meetings"):
                    return
                tosend = client.election.handle_vote(user,pieces[1]) or tosend
        elif pieces[0] == "!stats":
            tosend = await member_stats(user,pieces[1] if len(pieces) > 1 else "") or tosend
        elif pieces[0] == "!dump":
            tosend = await get_channel_messages(user,pieces[1] if len(pieces) > 1 else "") or tosend
        elif pieces[0] == '!nonmembers':
            tosend = get_nonmembers(user) or tosend
    await send_dm(user,tosend)

@officers_only
async def member_stats(user,command):
    command = parse_username_and_friend(command)
    if not command:
        return ("Invalid input\nusage: `!stats randomUser#0000 [action]`\nActions:\n\t- `activities`: see if user is involved in any current activities\n"
                "\t- `avatar`: display user's avatar\n"
                "\t- `created`: see when an account was created\n"
                "\t- `history`: get user's message history with bot\n"
                "\t- `id`: get user's unique ID\n"
                "\t- `isbot`: tell if user is a bot\n"
                "\t- `joined`: see when a user joined the affiliated server\n"
                "\t- `roles`: get user's role list\n"
                "\t- `toprole`: get user's role with the highest permissions\n")
    member = discord.utils.get(client.guild.members,name=command[0].split('#')[0],discriminator=command[0].split('#')[1])
    role_name_list = [role.name for role in member.roles]
    if not member:
        return f"{command[0]} not found in affiliated server."
    if command[1] == "roles":
        return member.roles
    elif command[1] == "joined":
        return arrow.get(member.joined_at).to('US/Central').isoformat(sep=' ')
    elif command[1] == "activities":
        return member.activities or "no activities"
    elif command[1] == "history":
        if "Officers" in role_name_list and member != user:
            return "Reading message history of other officers is forbidden."
        history = await member.history().flatten()
        for h in history:
            if isinstance(h.content,str):
                # don't show message history if invalid or a private vote/nominations
                if not ("flags=<MessageFlags " in h.content or "!vote" in h.content or "!nominate" in h.content):
                    messagestr = f"**{h.author.name}#{h.author.discriminator} "
                    channel = h.channel
                    if hasattr(channel,'recipient'):
                        messagestr += f"-> {h.channel.recipient.name}#{h.channel.recipient.discriminator}: "
                    else:
                        messagestr += f"-> {h.channel.name}: "
                    messagestr += f"** '{h.content}'"
                    await send_dm(user,messagestr)
        return "**end history**" if history else "no history"
    elif command[1] == "toprole":
        return member.top_role
    elif command[1] == "avatar":
        return member.avatar_url
    elif command[1] == "isbot":
        if member.bot:
            return f"{member.name} is a bot."
        else:
            return f"{member.name} is **not** a bot."
    elif command[1] == "created":
        return arrow.get(member.created_at).to('US/Central').isoformat(sep=' ')
    elif command[1] == "id":
        return member.id
    return member

@officers_only
async def get_channel_messages(user,params):
    if not params.strip() or params.strip().count(' ') != 0:
        return "Invalid input\nusage: `!dump [channel_name]`"
    channel = discord.utils.get(client.guild.channels,name=params.strip())
    if not channel:
        return f"Could not find channel {params}"
    me = discord.utils.get(client.guild.members,name=client.user.name,discriminator=client.user.discriminator)
    if not (channel.permissions_for(me).read_message_history and channel.permissions_for(me).read_messages):
        return f"Unable to read history for {channel.name}"
    history = await channel.history(limit=None).flatten()
    all_history = []
    last_time = None
    if not history or len(history) == 0:
        return f"No message history for {channel.name}"
    for i,h in enumerate(history):
        messagestr = ''
        current_time = arrow.get(h.created_at)
        if (not last_time) or (current_time.day != last_time.day) or (current_time.month != last_time.month) or (current_time.year != last_time.year):
            last_time = current_time
            if i != len(history)-1:
                messagestr += "\n"
            messagestr += f"[ {current_time.format('MM-DD-YYYY')} ]\n\n"
        messagestr += f"<{h.author.name}#{h.author.discriminator}"
        if hasattr(h.author,'nick') and h.author.nick:
            messagestr += f" ({h.author.nick})"
        messagestr += f"> {current_time.format('HH:mm:ss')}: {h.content}"
        all_history.append(messagestr)
    all_history.reverse()
    newfile = make_file(f"{client.guild.name}-{channel.name}-{arrow.utcnow().format('YYYY-MM-DD_HH-mm-ss')}.txt".replace(' ','_'),'\n'.join(all_history))
    await send_dm(user,discordfile=newfile)
    os.remove(f"/tmp/{newfile.filename}")
    return f'dumped chat log for {channel.name}'

@officers_only
def get_nonmembers(user):
    tosend = ''
    for member_id in client.non_members:
        member = discord.utils.get(client.guild.members,id=member_id)
        tosend += f'{member.nick or member.name} ({member.name}#{member.discriminator}), '
    return tosend

async def alert_nonmembers():
    rules_channel_id = discord.utils.get(client.guild.channels,name='rules').id
    accept_rules_id = discord.utils.get(client.guild.channels,name='accept-rules-here').id
    for member_id in client.non_members:
        member = discord.utils.get(client.guild.members,id=member_id)
        await send_dm(member,(f"Hi! We at the {client.clubname} noticed you hadn't accepted"
                            " the rules yet for our server.\n\nPlease first read the rules"
                            f" in <#{rules_channel_id}>, then visit the <#{accept_rules_id}>"
                            " channel and type `I accept` to get full access to the server.\nIf you"
                            " would like to leave the server, you may do so."))