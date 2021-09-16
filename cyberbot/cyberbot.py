# cyberbot.py - main class for CyberBot client
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

import os
import discord
from discord.ext import tasks
import arrow
from dataclasses import dataclass, field
from typing import List
import pickle

#
# you need to set the following values in your bash environment variables:
#   DISCORD_TOKEN, DISCORD_GUILD
# and these if using email verification
#   DISCORD_GMAIL, DISCORD_GMAIL_PASSWORD, DISCORD_EMAIL_ORGANIZATION
#

@dataclass
class Session:
    flags: List[dict] = field(default_factory=list)
    react_watch_list: List[dict] = field(default_factory=list)


class CyberBot(discord.Client):

    guild = None
    election = None
    allowed_bots = ["CyberBot"]
    session_data = Session()
    datafile = None
    non_members = []


    def __init__(self,clubname="generic club",datafile=None,*args,**kwargs):
        intents = discord.Intents.default()
        intents.members = True # for seeing members of the server
        self.guild_name = os.getenv('DISCORD_GUILD')
        self.token = os.getenv('DISCORD_TOKEN')
        super(self.__class__,self).__init__(intents=intents,*args,**kwargs)
        self.clubname = clubname
        self.datafile = datafile


    async def on_ready(self):
        self.load_session()
        self.guild = discord.utils.find(lambda g: g.name == self.guild_name, self.guilds)
        print(f'{self.user} is connected to the following guild:\n'f'{self.guild.name}(id: {self.guild.id})')
        print(f'Server has {len(self.guild.members)} members.')
        # populate non-members list
        for member in self.guild.members:
            roles = [role.name for role in member.roles]
            if not ("Member" in roles or "CyberBot" in roles):
                self.non_members.append(member.id)
        print(f"There are currently {len(self.non_members)} non-members in the server.")
        self.scheduled_tasks.start()


    async def on_message(self, message):
        from .channels import handle_election_channel, handle_rule_accept_channel
        from .dm import handle_dm
        from .verification import handle_verification_channel
        if message.author == self.user:
            return
        if isinstance(message.channel, discord.DMChannel):
            await handle_dm(user=message.author,msg=message.content)
            return
        if message.channel.name == "accept-rules-here":
            await handle_rule_accept_channel(message,'Member')
        elif message.channel.name == "elections":
            await handle_election_channel(message)
        elif message.channel.name == "verification":
            await handle_verification_channel(message)


    async def on_message_edit(self,before,after):
        from .channels import handle_rule_accept_channel
        if after.author == self.user:
            return
        if after.channel.name == "accept-rules-here":
            await handle_rule_accept_channel(after,'Member')


    async def on_raw_reaction_add(self,payload):
        for item in self.session_data.react_watch_list:
            if item['id'] == payload.message_id and payload.emoji.name == item['emote']:
                from .reactions import handle_reaction
                await handle_reaction(payload,item)


    async def on_raw_reaction_remove(self,payload):
        for item in self.session_data.react_watch_list:
            if item['id'] == payload.message_id and payload.emoji.name == item['emote']:
                from .reactions import handle_reaction
                await handle_reaction(payload,item,inverse=True)


    async def on_member_join(self, member):
        # prevent other bots from being invited in
        roles = [role.name for role in member.roles]
        is_allowed = False
        for bot in self.allowed_bots:
            if bot in roles:
                is_allowed = True
                break
        if member.bot and not is_allowed:
            print(f"kicking {member.name} for being a bot")
            member.kick(reason="No bot users allowed on this server.")
            return
        # go ahead and set user as non-member status
        self.non_members.append(member.id)


    async def on_member_remove(self,member):
        # remove user from self.non_members if they leave without accepting the rules
        if member.id in self.non_members:
            self.non_members.remove(member.id)


    def start_election_instance(self):
        from .voting import Voting
        self.election = Voting(self.clubname)


    def end_election_instance(self):
        self.election = None


    @tasks.loop(seconds=60.0)
    async def scheduled_tasks(self):
        current_time = arrow.now('US/Central').format('ddd-HH:mm')
        if current_time == 'Sat-12:00':
            from .dm import alert_nonmembers
            await alert_nonmembers()


    def load_session(self):
        if not (self.datafile and os.path.isfile(self.datafile)):
            return # file will be created later with pickle.dump()
        with open(self.datafile,'rb') as fp:
            data = pickle.load(fp)
        self.session_data = data
        print(f'loaded session data: {str(self.session_data)}')


    def update_session(self, item, data=None, append=False):
        try:
            sess_item = getattr(self.session_data,item)
        except(AttributeError):
            print(f"[!] Failed to update {item} in session data.")
            return
        if data == None and not append: # handle normal file update
            data = sess_item
        if append:
            sess_item.append(data)
        else:
            sess_item = data
        with open(self.datafile,'wb') as fp:
            pickle.dump(self.session_data,fp)


    def run(self,*args,**kwargs):
        super(self.__class__,self).run(self.token,*args,**kwargs)
