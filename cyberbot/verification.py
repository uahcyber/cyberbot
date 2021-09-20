# verification.py - functions for email verification
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
from .run import client
import smtplib
import ssl
import time
from .utils import officers_only
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from random import randint

blocked_emails = [
    'uahcybersec@uah.edu',
    ]

async def handle_verification(message):
    if message.author.id in [x["id"] for x in client.session_data.verified_users]:
        await message.reply("You are already verified. Congrats!")
        return
    split_msg = message.content.strip().split(' ',1)
    if len(split_msg) != 2:
        await message.reply("Invalid command.")
        return
    email = split_msg[1]
    if email in blocked_emails:
        await message.reply("Invalid email.")
        return
    if message.author in client.pending_verifies:
        await check_code(message)
        return
    if email[-len(client.organization):] == client.organization and " " not in email:
        await send_code(message)
        await message.reply(f"Sent verification code to {email}")
    else:
        await message.reply(f"Your email must me associated with {client.organization}")


# send a verification code to the email the user entered
async def send_code(email):
    sender_email = os.getenv("DISCORD_GMAIL")
    sender_password = os.getenv("DISCORD_GMAIL_PASSWORD")

    code = str(randint(0, 999999)).zfill(6)
    expire = time.time() + 60*15
    receiver_email = email.content.strip().split(' ',1)[1]
    message = MIMEMultipart("alternative")
    message["Subject"] = f"{client.clubname} Discord Verification"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Creates html message and text version for if html isn't supported
    text = f"""\
    Verification code command:
    !verify {code}
    Send the above command in a direct message to the CyberBot.
    You received this message because someone tried to verify their identity with this email address.
    If this was not you, ignore this message.

    Code is valid for 15 minutes.
    """
    html = f"""\
    <html>
      <body>
        <p><strong>Verification code command:</strong><br /><br />
        <strong><code style="border: solid; background-color: #00bbaa; color: white; border-color: black; margin: 5px; padding: 5px 10px 5px 10px;font-size:2em;">!verify {code}</code></strong><br /><br />
        Send the above command in a direct message to the CyberBot.<br />
        You received this message because someone tried to verify their identity with this email address.<br />
        If this was not you, ignore this message.<br /><br />Code is valid for 15 minutes.</p>
      </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, sender_password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
    # code expires in 15 minutes
    client.pending_verifies[email.author] = {"code": code, "expiration": expire, "email": receiver_email, "attempts": 0}
    print(f"User {email.author} sent verification code {code} to {receiver_email}")


# Check if a code is valid
async def check_code(message):
    server_user = discord.utils.get(client.guild.members,id=message.author.id)
    code = message.content.strip().split(' ',1)[1]
    is_expired = client.pending_verifies[message.author]["expiration"] < time.time()
    reply_msg = "Invalid code."
    if client.pending_verifies[message.author]["attempts"] > 10: # allow 10 attempts
        await message.reply("Too many verification attempts detected. Please contact an Officer to help you out.")
        return
    client.pending_verifies[message.author]["attempts"] += 1
    if str(client.pending_verifies[message.author]["code"]) == code:
        if not is_expired:
            await server_user.add_roles(discord.utils.get(client.guild.roles, name="Verified Student"))
            reply_msg = "You have been successfully verified."
            client.update_session('verified_users',{"id": server_user.id, "email": client.pending_verifies[message.author]["email"]},append=True)
            print(f"Successfully verified {server_user} as {client.pending_verifies[message.author]['email']}.")
        del client.pending_verifies[message.author]
    await message.reply(reply_msg)

def get_verified_users():
    if len(client.session_data.verified_users) == 0:
        return "no verified users"
    tosend = "Verified users:\n\n"
    for u in client.session_data.verified_users:
        tosend += f"  • <@{u['id']}>: {u['email']}\n"
    return tosend

def get_pending_verifications():
    if len(client.pending_verifies) == 0:
        return "no pending verifications"
    tosend = "Pending verifications:\n\n"
    for author,data in client.pending_verifies.items():
        tosend += f"  • <@{author.id}>: {data['email']} with code `{data['code']}` ({data['attempts']}/10 attempts)"
    return tosend

def get_verification_index_of_user(user):
    for i, data in enumerate(client.session_data.verified_users):
        if data["id"] == user.id:
            return i
    return -1

def remove_pending(username):
    user = discord.utils.get(client.guild.members, name=username.split('#')[0], discriminator=username.split('#')[1])
    del client.pending_verifies[user]

async def remove_verification(username):
    user = discord.utils.get(client.guild.members, name=username.split('#')[0], discriminator=username.split('#')[1])
    verification_idx = get_verification_index_of_user(user)
    if verification_idx == -1:
        return False
    del client.session_data.verified_users[verification_idx]
    client.update_session('verified_users')
    await user.remove_roles(discord.utils.get(client.guild.roles, name="Verified Student"))
    return True

@officers_only
async def verifications(user, msg):
    pieces = msg.split(" ")
    tosend = "Invalid input."
    if pieces[0] == "getVerified":
        tosend = get_verified_users()
    elif pieces[0] == "getPending":
        tosend = get_pending_verifications()
    elif pieces[0] == "rmPending" and len(pieces) == 2:
        if "#" not in pieces[1]:
            return tosend
        remove_pending(pieces[1])
        tosend = f"Removed {pieces[1]} from pending verifications."
    elif pieces[0] == "rmVerification": # revoke a verification
        if "#" not in pieces[1]:
            return tosend
        removed = await remove_verification(pieces[1])
        if not removed:
            tosend = f"Failed to remove verification for {pieces[1]}"
        else:
            tosend = f"Successfully removed verification status for {pieces[1]}"
    elif pieces[0] == "help":
        tosend = ( "usage: `!verifications [action] [OPTIONS]`\nActions:\n"
            "\t- `getVerified`: display a list of all verified users\n"
            "\t- `getPending`: display a list of all pending verifications\n"
            "\t- `rmPending [user#discriminator]`: delete a pending verification\n"
            "\t- `rmVerification [user#discriminator]`: remove a user's verification status\n")
    return tosend