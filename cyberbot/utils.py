# utils.py - various utility functions for CyberBot
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
import functools
from .run import client

def officers_only(func):
    @functools.wraps(func)
    async def wrapper(*args,**kwargs):
        roles = []
        for arg in args:
            if isinstance(arg,discord.Member):
                roles = [role.name for role in arg.roles]
                break
            elif isinstance(arg,discord.Message):
                user = discord.utils.get(client.guild.members,name=arg.author.name,discriminator=arg.author.discriminator)
                roles = [role.name for role in user.roles]
                break
        if "Officers" in roles:
            return await func(*args, **kwargs)
        return
    return wrapper

async def send_dm(user,msg=None,discordfile=None):
    dm = user.dm_channel
    if dm is None:
        await user.create_dm()
        dm = user.dm_channel
    await dm.send(msg,file=discordfile)

def make_file(name,content):
    filename = f"/tmp/{name}"
    discordfile = None
    with open(filename,'w') as fp:
        fp.write(content)
    with open(filename,'r') as fp:
        discordfile = discord.File(fp,filename=name)
    return discordfile

def parse_username_and_friend(toparse):
    toparse = toparse.strip()
    if ("#" not in toparse) or (toparse.count('#') > 1):
        return None
    halved = toparse.rsplit(' ',1)
    if len(halved) != 2:
        return None
    return halved

def diff_lists(a, b):
    return (list(list(set(a)-set(b)) + list(set(b)-set(a))))