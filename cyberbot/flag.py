# flag.py - deals with capture the flag infrastructure
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
from .utils import flag_regex

def get_flag(topic=None,index=False,solvers=False,all_data=False):
    if topic:
        for i,flag in enumerate(client.session_data.flags):
            if topic == flag["topic"]:
                if all_data:
                    return (i, flag["flag"], flag["solvers"])
                elif index and solvers:
                    return (i, flag["solvers"])
                elif index:
                    return i
                elif solvers:
                    return flag["solvers"]
                else:
                    return flag["flag"]
        return None
    return client.session_data.flags

def add_flag(topic,flag):
    flag_str = f"uah{{{flag.strip()}}}" if not flag_regex.match(flag) else flag
    topics = [f["topic"] for f in client.session_data.flags]
    if topic in topics: # no duplicate topics
        return False
    client.update_session('flags', {"topic": topic.strip(), "flag": flag_str, "solvers": []}, append=True)
    return True

def check_flag(data):
    for flag in client.session_data.flags:
        if data == flag["flag"]:
            return flag["topic"]
    return None

def add_solve(topic,user):
    index, solvers = get_flag(topic=topic,index=True,solvers=True)
    if user.id in solvers:
        return False
    client.session_data.flags[index]["solvers"].append(user.id)
    client.update_session('flags')
    return True

def change_flag(topic,new_flag):
    client.session_data.flags[get_flag(topic=topic,index=True)]["flag"] = new_flag
    client.update_session('flags')

def delete_flag(topic):
    del client.session_data.flags[get_flag(topic=topic,index=True)]
    client.update_session('flags')