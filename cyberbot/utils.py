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
import re
from .run import client

discord_tag_regex = r"\w+#\d{4}"

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

def clean_vote_message(content,author):
    if author == client.user: # from bot:
        content = re.sub(discord_tag_regex,"[REDACTED]",content)
        if "cast for" in content:
            content = content.split("cast for")[0] + "cast for [REDACTED]!"
        elif "does not meet the qualifications" in content:
            content = "[REDACTED] does not meet the qualifications" + content.split("does not meet the qualifications")[1]
        elif "Cancelled nomination for" in content:
            content = "Cancelled nomination for [REDACTED], you still have 1 nomination to use on someone else."
        elif "Seconded nomination of" in content:
            content = "Seconded nomination of [REDACTED] for position" + content.split("for position")[1]
        elif "has already accepted" in content:
            content = "[REDACTED] has already accepted" + content.split('has already accepted')[1]
        elif "**rejected** your nomination" in content:
            content = "[REDACTED] **rejected** your nomination" + content.split('**rejected** your nomination')[1]
        elif "has **accepted**" in content:
            content = "[REDACTED] has **accepted**" + content.split('has **accepted**')[1]
        elif "[REDACTED]" not in content and "was not found" in content:
            content = "[REDACTED] was not found" + content.split('was not found')[1]
    else: # from user
        if "!vote" in content or "!nominate" in content:
            content = re.sub(discord_tag_regex,"[REDACTED]",content)
    return content