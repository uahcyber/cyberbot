# voting.py - classes used for holding officer elections
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
from dataclasses import dataclass, field
from typing import List
from .run import client
from .voice import members_in_voice_channel
from .utils import diff_lists, send_dm, parse_username_and_friend

@dataclass
class Nomination:
    user: str
    position: str
    statement: str
    by: List[int] = field(default_factory=list)


@dataclass
class Candidate:
    user: str
    position: str
    votes: int = 0

    def add_vote(self):
        self.votes = self.votes + 1


@dataclass
class PositionList:
    position: str
    users: List[Candidate] = field(default_factory=list)


@dataclass
class Voter:
    user: str
    positions: List[str] = field(default_factory=list) # positions that this user has voted for


class Voting:

    name: str
    positions_to_elect = []
    nominations = []
    candidates = []
    voters = []
    users_waiting_for_nom = []
    usersWaitingForStatement = []
    messages = []
    eligible_members = []


    def __init__(self,clubname):
        self.clubname = clubname
        self.nomination_started = False
        self.election_started = False


    def handle_vote(self,user,params):
        bad_input = "Incorrect input, please try again."
        pieces = parse_username_and_friend(params)
        if not (pieces and len(pieces) == 2):
            return bad_input
        userRoles = [role.name for role in user.roles]
        if "Verified Student" not in userRoles:
            return "You must be a Verified Student to use the voting function."
        username = pieces[0]
        position = pieces[1].lower()
        candidate = discord.utils.get(client.guild.members, name=username.split('#')[0], discriminator=username.split('#')[1])
        for voter in self.voters:
            if voter.user == user.id:
                if voter.positions == self.positions_to_elect: # voter has voted for every needed position
                    return "You have voted for all positions in this election. Please wait for everyone else to submit their votes."
                if position in voter.positions:
                    # user has already voted for this position
                    return f"You have already voted for the position of {position} in this election. Votes are final."
        if not candidate:
            return f"{username} was not found in the {self.clubname} server!"
        castvote = False
        for cand in self.candidates:
            if cand.user == candidate.id:
                if cand.position == position:
                    # vote for candidate
                    cand.add_vote()
                    voter_exists = False
                    for voter in self.voters:
                        # find user and record vote for position
                        if voter.user == user.id:
                            voter_exists = True
                            voter.positions.append(cand.position)
                            break
                    if not voter_exists:
                        v = Voter(user.id,[cand.position])
                        self.voters.append(v)
                    castvote = True
                    break
        self.__update_election_session_data()
        if castvote:
            return f"Vote for {position.capitalize()} cast for {candidate.name}!"
        return f"Unable to cast vote for {candidate.name} for the position of {position.capitalize()}."


    def get_votes(self):
        # make sure all positions are voted for
        if not self.election_started:
            return "The election period has not started yet."
        positions_with_votes = set()
        for cand in self.candidates:
            if cand.votes > 0:
                positions_with_votes.add(cand.position)
        if positions_with_votes != set(self.positions_to_elect):
            return "All positions have not been voted for."
        final_results_fmt = "\nElection Results\n=====================\n\n"
        winners = []
        for position in self.__sort_candidate_votes(): # returns PositionList
            final_results_fmt += f'Position: **{position.position.capitalize()}**\n'
            for i,cand in enumerate(position.users):
                thisUser = discord.utils.get(client.guild.members, id=cand.user)
                final_results_fmt += f"\t- "
                if i == 0:
                    final_results_fmt += f'**{thisUser.display_name}\t\t {cand.votes} votes\n\t\t<@{cand.user}> is the new {position.position.capitalize()}!**\n'
                    winners.append({"user":thisUser, "position": position.position})
                else:
                    final_results_fmt += f'{thisUser.name}\t\t {cand.votes} votes\n'
            final_results_fmt += "\n"
        self.__update_election_session_data()
        return final_results_fmt


    def get_nominations(self):
        if len(self.nominations) == 0:
            return "No one has been nominated yet. Check back later!"
        fmtstr = "\nNominations\n=====================\n"
        all_noms = [] # list of {"position": "president", "users": [{"user": dayt0n#5130", "noms": 2}]}
        for nom in self.nominations:
            exists = False
            for item in all_noms:
                if nom.position == item.position:
                    item.users.append(nom.user)
                    exists = True
                    break
            if not exists:
                cand = Candidate(nom.user,nom.position,len(nom.by))
                new_nom_position = PositionList(nom.position,[cand])
                all_noms.append(new_nom_position)
        for nom in all_noms:
            fmtstr += f"Position: **{nom.position.capitalize()}**\n"
            for user in nom.users:
                thisUser = discord.utils.get(client.guild.members, id=nom.user)
                plural = "s" if user.votes > 1 else ""
                fmtstr += f"\t<@{user.user}>: {user.votes} nomination{plural}\n\t\tVote command: `!vote {thisUser.name}#{thisUser.discriminator} {nom.position.capitalize()}`\n"
            fmtstr += "\n"
        return fmtstr


    async def handle_nominate(self,user,params):
        nomexists = False
        bad_input = "Incorrect input, please try again."
        pieces = parse_username_and_friend(params)
        tosend = None
        if not (pieces and len(pieces) == 2):
            return bad_input
        userRoles = [role.name for role in user.roles]
        if "Verified Student" not in userRoles:
            return "You must be a Verified Student to use the nomination function."
        username = pieces[0]
        position = pieces[1].lower()
        if position not in self.positions_to_elect:
            return "Position is not up for election."
        nominee = discord.utils.get(client.guild.members, name=username.split('#')[0], discriminator=username.split('#')[1])
        if not nominee:
            return f"User {username} was not found in the {self.clubname} server!"
        for nom in self.nominations:
            if user.id in nom.by:
                return "You have already nominated someone for a position."
            if nom.user == nominee.id:
                self.users_waiting_for_nom.append(user.id)
                await send_dm(user, f"{nominee.name} has already accepted the nomination for **{nom.position}**. To second this nomination, please reply with:\n`!nominate second`\nOtherwise, reply with:\n`!nominate cancel`")
                while True:
                    def dmCheck(m):
                        return isinstance(m.channel, discord.DMChannel) and m.author.id == user.id
                    msg = await client.wait_for('message',check=dmCheck)
                    msg = msg.content.rstrip().lower().split(' ')
                    if msg[0] == "!nominate" and len(msg) == 2:
                        if msg[1] == 'second':
                            nom.by.append(user.id)
                            tosend = f"Seconded nomination of {nominee.name} for position of {position.capitalize()}!"
                            self.users_waiting_for_nom.append(user.id)
                            break
                        elif msg[1] == 'cancel':
                            self.users_waiting_for_nom.remove(user.id)
                            return f"Cancelled nomination for {nominee.name}, you still have 1 nomination to use on someone else."
                    await send_dm(user, bad_input)
                nomexists = True
        if not nomexists:
            if nominee.id not in self.eligible_members:
                return f"{nominee.name} does not meet the qualifications for an officer position in the {self.clubname}."
            self.users_waiting_for_nom.append(user.id)
            if nominee != user:
                await send_dm(nominee, f"You have been nominated for the officer position: {position.capitalize()} of the UAH Cybersecurity Club!\nIf you accept, please indicate as such by replying with:\n`!nominate accept`\nIf you do **NOT** accept, reply with:\n`!nominate reject`")
                while True:
                    def dmCheck(m):
                        return isinstance(m.channel, discord.DMChannel) and m.author.id == nominee.id
                    msg = await client.wait_for('message',check=dmCheck)
                    msg = msg.content.rstrip().lower().split(' ')
                    if msg[0] == '!nominate' and len(msg) == 2:
                        if msg[1] == 'reject':
                            self.users_waiting_for_nom.remove(user.id)
                            self.__update_election_session_data()
                            return f"{nominee.name} **rejected** your nomination for {position.capitalize()}."
                        elif msg[1] == 'accept':
                            break
                    await send_dm(nominee, bad_input)
            else:
                tosend = f"You have successfully nominated yourself for {position.capitalize()}!"
            await send_dm(nominee, f"Please send a message stating your intentions as {position.capitalize()}. This is your chance to convince people to vote for you. You can only answer this prompt once.")
            self.usersWaitingForStatement.append(nominee.id)
            def dmCheck(m):
                return isinstance(m.channel, discord.DMChannel) and m.author.id == nominee.id
            msg = await client.wait_for('message',check=dmCheck)
            nom = Nomination(nominee.id,position,msg.content,[user.id])
            self.nominations.append(nom)
            ec = discord.utils.get(client.guild.channels,name=client.electionChannel)
            if ec:
                nomStr = f"Nomination: **{position.capitalize()}**\n"
                await ec.send(f"{nomStr}" + "="*(len(nomStr)-5) + f"\nMember: <@{nominee.id}> (`{nominee.name}#{nominee.discriminator}`)\nCampaign Statement:\n```\n{nom.statement}\n```")
            self.usersWaitingForStatement.remove(nominee.id)
        tosend = tosend or f"{nominee.name} has **accepted** your nomination for {position.capitalize()}!"
        self.users_waiting_for_nom.remove(user.id)
        self.__update_election_session_data()
        return tosend
        

    async def start_nomination(self,pieces):
        if not pieces:
            return "Please specify the name of the election and positions to add.\nExample:\n\t`!nomination start SP2022 Treasurer President Secretary`"
        # 0, 1 indices are !nomination start
        if self.nomination_started:
            # already started
            return "The nomination period has already started.\nTo restart, run:\n\t`!nomination stop clear`\nthen,\n\t`!nomination start`"
        self.name = pieces.pop(0)
        # do election session stuff here
        self.positions_to_elect.extend([pos.lower() for pos in pieces])
        #await self.__populate_messages()
        self.eligible_members = self.__get_eligible_members()
        if not self.eligible_members:
            # no one is eligible, cannot do nominations
            self.positions_to_elect.clear()
            self.messages.clear()
            self.eligible_members.clear()
            return "No members are eligible for positions at the moment. Make sure those who plan on running are in attendance."
        self.nomination_started = True
        if not self.__does_election_exist_in_session():
            client.update_session('electionData', {self.name: [self.positions_to_elect, self.nominations, self.candidates, self.voters, self.users_waiting_for_nom, self.usersWaitingForStatement, self.eligible_members, self.election_started, self.nomination_started]}, append=True)
        return self.__get_nomination_start_string()


    def stop_nomination(self,pieces=None):
        tosend = "The nomination period has ended" if self.nomination_started else "The nomination period has not started"
        if pieces == "clear":
            self.positions_to_elect.clear()
            self.nominations.clear()
            self.messages.clear()
            self.eligible_members.clear()
            tosend += ", positions up for election have been cleared"
            self.nomination_started = False
            return tosend + '.'
        for pos in self.positions_to_elect:
            position_nominated = False
            for nom in self.nominations:
                if pos == nom.position:
                    position_nominated = True
                    break
            if position_nominated:
                continue
            return "There are still empty positions that do not have nominees, nominations will continue."
        self.eligible_members.clear()
        self.messages.clear()
        self.nomination_started = False
        self.__update_election_session_data()
        return tosend + '.'


    def start_election(self):
        tosend = ''
        if self.nomination_started:
            tosend = self.stop_nomination() + "\n"
            if "empty positions" in tosend:
                return tosend
        # move nominees to candidate status
        if not self.nominations:
            return "No one has been nominated for any position, not starting election."
        for nom in self.nominations:
            cand = Candidate(nom.user,nom.position)
            self.candidates.append(cand)
        self.election_started = True
        tosend += self.__get_vote_start_string()
        self.__update_election_session_data()
        return tosend


    def stop_election(self):
        for pos in self.positions_to_elect:
            position_decided = False
            for cand in self.candidates:
                if pos == cand.position and cand.votes > 0:
                    position_decided = True
                    break
            if position_decided:
                continue
            return "All positions have not yet been voted for, election will continue."
        results = self.get_votes()
        self.election_started = False
        self.__update_election_session_data()
        return "Election has ended.\n" + results


    def delete_nomination(self,nomineeId):
        for i,nom in enumerate(self.nominations):
            if nom.user == nomineeId:
                del self.nominations[i]
                return True
        return False
    
    def __get_eligible_members(self):
        eligible = []
        for member in client.guild.members:
            if self.__is_member_eligible(member):
                eligible.append(member.id)
        return eligible


    def __sort_candidate_votes(self):
        results = []
        for position in self.positions_to_elect:
            pos = PositionList(position)
            all_cands = []
            for cand in self.candidates:
                if cand.position == position:
                    all_cands.append(cand)
            pos.users = sorted(all_cands, key = lambda i: i.votes, reverse=True)
            results.append(pos)
        return results


    def __is_member_eligible(self,nominee, msg_count=6, semester_length=16):
        #now = arrow.get('2020-12-10T00:00:00.00+00:00')# last day of semester #arrow.utcnow() 
        # must be presently enrolled at university
        nom_roles = [role.name for role in nominee.roles]
        if "Alum" in nom_roles or "Verified Student" not in nom_roles:
            return False
        # must be a member for at least 1 semester
        #if nominee.joined_at:
        #    member_for = (now - arrow.get(nominee.joined_at)).days
        #    if member_for < (semester_length * 7):
        #        return False
        # user should have sent a certain number of messages in the past semester
        # checks if half of the messages were sent in the first half of the semester and half in the last
        #nom_msgs = [x for x in self.messages if (x.author.id == nominee.id) and ((now - arrow.get(x.created_at)).days < semester_length * 7)]
        #first_half_msgs = [x for x in nom_msgs if (arrow.get(x.created_at)) < now.shift(weeks=-semester_length/2)]
        #if (len(first_half_msgs) < msg_count//2) or (len(diff_lists(nom_msgs,first_half_msgs)) < (msg_count - (msg_count//2))):
        #    return False
        return True


    def __get_nomination_start_string(self):
        memberlist = 'Eligible members for nomination:\n'
        for member in self.eligible_members:
            thisMember = discord.utils.get(client.guild.members, id=member)
            memberlist += f'\t- <@{member}> (`{thisMember.name}#{thisMember.discriminator}`)\n'
        position_list = ''
        for pos in self.positions_to_elect:
            position_list += f'\t- **{pos.capitalize()}**\n'
        return  (f"{memberlist}\n\nNominations may now begin.\nPositions up for election:\n\n{position_list}\nInstructions:\n"
                    f"Send a **direct message** to <@{client.user.id}> specifying who, if anyone, you would "
                    "like to nominate in the following format:\n\t`!nominate [full user id] [position]`\n"
                    "Example nominations:\n\t`!nominate ClubMember#1234 Treasurer`\n\t`!nominate Other ClubMember#1234 Treasurer`")


    def __get_vote_start_string(self):
        position_list = ''
        for pos in self.positions_to_elect:
            position_list += f'\t- **{pos.capitalize()}**\n'
            for cand in self.candidates:
                thisCand = discord.utils.get(client.guild.members, id=cand.user)
                if cand.position == pos:
                    position_list += f'\t\t- <@{cand.user}>\n\t\t  vote command: `!vote {thisCand.name}#{thisCand.discriminator} {pos.capitalize()}`\n'
        return (f"Votes may now be cast.\nPositions up for election and their candidates:\n\n{position_list}\nInstructions:\n"
                    f"Send a **direct message** to <@{client.user.id}> specifying who you want to elect"
                    "by sending the associated `!vote` command as listed above.")
    

    def __does_election_exist_in_session(self):
        for e in client.session_data.electionData:
            if self.name in e.keys():
                return True
        return False
    
    def __update_election_session_data(self):
        for i, e in enumerate(client.session_data.electionData):
            if self.name in e.keys():
                dataCopy = client.session_data.electionData.copy()
                dataCopy[i] = {self.name: [self.positions_to_elect, self.nominations, self.candidates, self.voters, self.users_waiting_for_nom, self.usersWaitingForStatement, self.eligible_members, self.election_started, self.nomination_started]}
                client.update_session('electionData', dataCopy)
                return
        raise KeyError(f"Election with name '{self.name}' not found in session data!")

    async def __populate_messages(self):
        for channel in client.guild.channels:
            if not (channel and isinstance(channel,discord.TextChannel)):
                continue
            me = discord.utils.get(client.guild.members,name=client.user.name,discriminator=client.user.discriminator)
            if not (channel.permissions_for(me).read_message_history and channel.permissions_for(me).read_messages):
                continue
            history = await channel.history(limit=None).flatten()
            if not history or len(history) == 0:
                continue
            self.messages.extend(history)
