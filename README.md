CyberBot
========

UAH Cybersecurity Club Discord bot

Features
--------

  * Assign membership on rule accepts
  * Assign verified role on email verification
  * Remind non-members to accept rules weekly
  * Officer commands
    * dump channel logs
  * Full club officer nomination/election system
    * Anonymous voting
    * Anonymous nominations
    * Officer eligibility requirements
    * Nominated member can accept or reject the nomination
    * No double voting for a specific nominee or position
  * Kick new bot users unless specifically allowed
  * Internal Capture The Flag (CTF)
  * Perform actions on a reaction to a watched message
    * Manage roles

Setup
-----

`pip3 install .`

You must set the following environment variables:

`DISCORD_TOKEN` - the token of the bot in the Discord Developer settings

`DISCORD_GUILD` - the name of the Discord Server to which the bot will be deployed

And these if using email verification:

`DISCORD_GMAIL` - the gmail account used to send verification emails

`DISCORD_GMAIL_PASSWORD` - the password for the gmail account

`DISCORD_EMAIL_ORGANIZATION` - the required email domain to verify

Examples:

```bash
DISCORD_TOKEN="j64f3UePWeSWRzSYIu.P00j6y.tzDTMObXakj9Kqof"
DISCORD_GUILD="My Server Name"
DISCORD_GMAIL="companydiscordverification@gmail.com"
DISCORD_GMAIL_PASSWORD="password"
```

You can optionally set the club name and email verification organization by passing the `clubname` and `org` parameters to `CyberBot()` in [cyberbot/run.py](cyberbot/run.py#L21).

Running
-------

To use the CTF and message reaction handling feature, you must specify a filename for session data when running the bot.

In a terminal, run:

`$ cyberbot [optional file location for storing session data]`
