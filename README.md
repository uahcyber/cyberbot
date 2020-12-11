CyberBot
========

UAH Cybersecurity Club Discord bot

Features
--------

  * Assign membership on rule accepts
  * Remind non-members to accept rules weekly
  * Officer commands
    * dump channel logs
  * Full club officer nomination/election system
    * Anonymous voting
    * Anonymous nominations
    * Officer eligibility requirements
    * Nominated member can accept or reject the nomination
    * No double voting for a specific nominee or position

Setup
-----

`pip3 install .`

You must set the following environment variables:

`DISCORD_TOKEN` - the token of the bot in the Discord Developer settings

`DISCORD_GUILD` - the name of the Discord Server to which the bot will be deployed

Examples:

```bash
DISCORD_TOKEN=j64f3UePWeSWRzSYIu.P00j6y.tzDTMObXakj9Kqof
DISCORD_GUILD="My Server Name"
```

You can optionally set the club name by passing the `clubname` parameter to `CyberBot()` in [cyberbot/run.py](cyberbot/run.py#L21).

Running
-------

In a terminal, run:

`$ cyberbot`
