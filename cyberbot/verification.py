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
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from random import randint

sender_email = os.getenv("DISCORD_GMAIL")
sender_password = os.getenv("DISCORD_GMAIL_PASSWORD")
organization = os.getenv("DISCORD_EMAIL_ORGANIZATION")
pending_verifies = {}


async def handle_verification_channel(message):
    if "@" in message.content:
        if organization in message.content.lower():
            await send_code(message)
            await message.reply(f"Sent verification code to {message.content}")
        else:
            await message.reply("Your email must contain uah.edu")
    else:
        await check_code(message)


# send a verification code to the email the user entered
async def send_code(email):
    code = randint(100000, 999999)

    receiver_email = email.content
    message = MIMEMultipart("alternative")
    message["Subject"] = f"{client.clubname} discord verification"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Creates html message and text version for if html isn't supported
    text = f"""\
    Verification code:
    {code}
    You received this message because someone tried to verify their identity with this email address.
    If this was not you, ignore this message.
    """
    html = f"""\
    <html>
      <body>
        <p><strong>Verification code:</strong><br /><br />
        <strong><code style="border: solid; background-color: #00bbaa; color: white; border-color: black; margin: 5px; padding: 5px 10px 5px 10px;font-size:2em;">{code}</code></strong><br /><br />
        You received this message because someone tried to verify their identity with this email address.<br />
        If this was not you, ignore this message.</p>
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

    pending_verifies[email.author] = code
    print(f"User {email.author} sent verification code {code} to {email.content}")


# Check if a code is valid
async def check_code(message):
    if not str(pending_verifies[message.author]) == message.content:
        await message.reply(f"This is not an active code")
    else:
        await message.author.add_roles(discord.utils.get(client.guild.roles, name="Verified"))
        await message.reply("You have been successfully verified.")