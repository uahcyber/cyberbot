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

#
# you need to set the following values in your bash environment variables:
#   DISCORD_TOKEN, DISCORD_GUILD
#

class CyberBot(discord.Client):

    guild = None
    election = None

    def __init__(self,clubname,*args,**kwargs):
        intents = discord.Intents.default()
        intents.members = True # for seeing members of the server
        super(self.__class__,self).__init__(intents=intents,*args,**kwargs)
        self.guild_name = os.getenv('DISCORD_GUILD')
        self.token = os.getenv('DISCORD_TOKEN')
        self.clubname = clubname

    async def on_ready(self):
        self.guild = discord.utils.find(lambda g: g.name == self.guild_name, self.guilds)
        print(f'{self.user} is connected to the following guild:\n'f'{self.guild.name}(id: {self.guild.id})')
        print(f'Server has {len(self.guild.members)} members.')
    
    async def on_message(self, message):
        from .channels import handle_election_channel, handle_rule_accept_channel
        from .dm import handle_dm
        if message.author == self.user:
            return
        if isinstance(message.channel, discord.DMChannel):
            await handle_dm(user=message.author,msg=message.content)
            return
        if message.channel.name == "accept-rules-here":
            await handle_rule_accept_channel(message,'Member')
        elif message.channel.name == "elections":
            await handle_election_channel(message)
    
    def start_election_instance(self):
        from .voting import Voting
        self.election = Voting(self.clubname)

    def end_election_instance(self):
        self.election = None

    def run(self,*args,**kwargs):
        super(self.__class__,self).run(self.token,*args,**kwargs)
