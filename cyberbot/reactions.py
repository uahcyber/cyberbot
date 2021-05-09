# reactions.py - handle message reaction actions
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

async def handle_reaction(reaction, action_item, inverse=False):
    if action_item["action"] == "setrole":
        await handle_setrole(reaction, action_item["data"], inverse=inverse)

async def handle_setrole(reaction, data, inverse=False):
    if '"' in data and data.count('"') == 2:
        role_name = data.split('"',1)[1].split('"',1)[0]
    elif ' ' in data:
        role_name = data.rsplit(' ')[1]
    else:
        role_name = data
    role = discord.utils.get(client.guild.roles,name=role_name)
    if not role:
        print(f"Could not find role with name '{role_name}'")
        return
    user = discord.utils.get(client.guild.members,id=reaction.user_id)
    if not user:
        print(f"Error getting user with id: '{reaction.user_id}'")
    # actually commit roles
    if inverse:
        await user.remove_roles(role)
        print(f"Removed role {role} from user {user}.")
    else:
        await user.add_roles(role)
        print(f"Added role {role} to user {user}.")