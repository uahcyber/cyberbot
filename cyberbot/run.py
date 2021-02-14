# run.py - main file for starting CyberBot
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

from .cyberbot import CyberBot
import sys

flagfile = None
if len(sys.argv) > 1:
    flagfile = sys.argv[1]

client = CyberBot(clubname="UAH Cybersecurity Club",flagfile=flagfile)

def main():
    client.run()

if __name__ == "__main__":
    main()