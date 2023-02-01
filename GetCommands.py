import re
import sys

def ReadBotPyAndGetCommands():
    with open('Bot.py', 'r') as f:
        lines = f.readlines()
        commands = []
        for line in lines:
            line = line.replace('or', '\n')
            if line.find('message.content.startswith') != -1 or line.find('message.content==') != -1:
                #reg to match message.content.startswith('value') and message.content=='value' and get the value
                reg = r"message\.content\.startswith\('(.*)'\)|message\.content=='(.*)'"
                match = re.search(reg, line)
                if match:
                    if match.group(1):
                        commands.append(match.group(1))
                    elif match.group(2):
                        commands.append(match.group(2))
        #join the commands with a space and print them

        return " ".join(commands)
print(ReadBotPyAndGetCommands())
