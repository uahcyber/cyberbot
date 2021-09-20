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
    email = message.content.strip().split(' ',1)[1]
    if email in blocked_emails:
        await message.reply("Invalid email.")
        return
    if message.author in client.pending_verifies:
        await check_code(message)
        return
    if email[len(client.organization)+1:] == client.organization and " " not in email:
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
    Verification code:
    {code}
    You received this message because someone tried to verify their identity with this email address.
    If this was not you, ignore this message.

    Code is valid for 15 minutes.
    """
    html = f"""\
    <html>
      <body>
        <p><strong>Verification code:</strong><br /><br />
        <strong><code style="border: solid; background-color: #00bbaa; color: white; border-color: black; margin: 5px; padding: 5px 10px 5px 10px;font-size:2em;">{code}</code></strong><br /><br />
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
    client.pending_verifies[email.author] = {"code": code, "expiration": expire, "email": receiver_email} 
    print(f"User {email.author} sent verification code {code} to {email.content}")


# Check if a code is valid
async def check_code(message):
    server_user = discord.utils.get(client.guild.members,id=message.author.id)
    code = message.content.strip().split(' ',1)[1]
    is_expired = client.pending_verifies[message.author]["expiration"] < time.time()
    reply_msg = "Invalid code."
    if str(client.pending_verifies[message.author]["code"]) == code:
        if not is_expired:
            await server_user.add_roles(discord.utils.get(client.guild.roles, name="Verified Student"))
            reply_msg = "You have been successfully verified."
            client.update_session('verified_users',{"id": server_user.id, "email": client.pending_verifies[message.author]["email"]},append=True)
        del client.pending_verifies[message.author]
    await message.reply(reply_msg)

@officers_only
async def get_verified_users(user):
    tosend = "Verified users:\n\n"
    for u in client.session_data.verified_users:
        tosend += f"  • <@{u['id']}>: {u['email']}\n"
    return tosend