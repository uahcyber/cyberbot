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
import pickle
import os.path
from .run import client
from .utils import flag_regex

def get_flag(topic=None,index=False,solvers=False,all_data=False):
    if topic:
        for i,flag in enumerate(client.flags):
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
    return client.flags

def load_flags():
    if not os.path.isfile(client.flagfile):
        return # file will be created later with pickle.dump()
    with open(client.flagfile,'rb') as fp:
        data = pickle.load(fp)
    client.flags = data

def add_flag(topic,flag):
    flag_str = f"uah{{{flag.strip()}}}" if not flag_regex.match(flag) else flag
    topics = [f["topic"] for f in client.flags]
    if topic in topics: # no duplicate topics
        return False
    client.flags.append({"topic": topic.strip(), "flag": flag_str, "solvers": []})
    with open(client.flagfile,'wb') as fp:
        pickle.dump(client.flags,fp)
    return True

def check_flag(data):
    for flag in client.flags:
        if data == flag["flag"]:
            return flag["topic"]
    return None

def add_solve(topic,user):
    index, solvers = get_flag(topic=topic,index=True,solvers=True)
    if user.id in solvers:
        return False
    client.flags[index]["solvers"].append(user.id)
    with open(client.flagfile,'wb') as fp: # commit changes
        pickle.dump(client.flags,fp)
    return True

def change_flag(topic,new_flag):
    client.flags[get_flag(topic=topic,index=True)]["flag"] = new_flag
    with open(client.flagfile,'wb') as fp:
        pickle.dump(client.flags,fp)

def delete_flag(topic):
    del client.flags[get_flag(topic=topic,index=True)]
    with open(client.flagfile,'wb') as fp:
        pickle.dump(client.flags,fp)