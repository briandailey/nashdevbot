"""
find.py - Willie Spelling correction module
Copyright 2011, Michael Yanovich, yanovich.net
Copyright 2013, Edward Powell, embolalia.net
Licensed under the Eiffel Forum License 2.

http://willie.dftba.net

Contributions from: Matt Meinwald and Morgan Goose
This module will fix spelling errors if someone corrects them
using the sed notation (s///) commonly found in vi/vim.
"""

import re
from willie.tools import Nick

def setup(willie):
    willie.memory['find_lines'] = dict()
    
def collectlines(willie, trigger):
    """Create a temporary log of what people say"""
    
    # Don't log things in PM
    if not trigger.sender.startswith('#'):
        return

    # Add a log for the channel and nick, if there isn't already one
    if trigger.sender not in willie.memory['find_lines']:
        willie.memory['find_lines'][trigger.sender] = dict()
    if Nick(trigger.nick) not in willie.memory['find_lines'][trigger.sender]:
        willie.memory['find_lines'][trigger.sender][Nick(trigger.nick)] = list()

    # Create a temporary list of the user's lines in a channel
    templist = willie.memory['find_lines'][trigger.sender][Nick(trigger.nick)]
    line = trigger.group()
    if line.startswith("s/"): # Don't remember substitutions
        return
    elif line.startswith("\x01ACTION"): # For /me messages
        line = line[:-1]
        templist.append(line)
    else:
        templist.append(line)

    del templist[:-10] # Keep the log to 10 lines per person
    
    willie.memory['find_lines'][trigger.sender][Nick(trigger.nick)] = templist
collectlines.rule = r'.*'
collectlines.priority = 'low'


def findandreplace(willie, trigger):
    # Don't bother in PM
    if not trigger.sender.startswith('#'):
        return
    
    # Correcting other person vs self.
    rnick = Nick(trigger.group(1) or trigger.nick)

    search_dict = willie.memory['find_lines']
    # only do something if there is conversation to work with
    if trigger.sender not in search_dict:
        return
    if Nick(rnick) not in search_dict[trigger.sender]:
        return

    #TODO rest[0] is find, rest[1] is replace. These should be made variables of
    #their own at some point.
    rest = [trigger.group(2), trigger.group(3)]
    rest[0] = rest[0].replace(r'\/', '/')
    rest[1] = rest[1].replace(r'\/', '/')
    me = False # /me command
    flags = (trigger.group(4) or '')
    
    # If g flag is given, replace all. Otherwise, replace once.
    if 'g' in flags:
        count = -1
    else:
        count = 1
    
    # repl is a lambda function which performs the substitution. i flag turns
    # off case sensitivity. re.U turns on unicode replacement.
    if 'i' in flags:
        regex = re.compile(re.escape(rest[0]),re.U|re.I)
        repl = lambda s: re.sub(regex,rest[1],s,count == 1)
    else:
        repl = lambda s: s.replace(rest[0],rest[1],count)

    # Look back through the user's lines in the channel until you find a line
    # where the replacement works
    for line in reversed(search_dict[trigger.sender][rnick]):
        if line.startswith("\x01ACTION"):
            me = True # /me command
            line = line[8:]
        else:
            me = False
        new_phrase = repl(line)
        if new_phrase != line: # we are done
            break

    if not new_phrase or new_phrase == line:
        return # Didn't find anything

    # Save the new "edited" message.
    action = (me and '\x01ACTION ') or '' # If /me message, prepend \x01ACTION
    templist = search_dict[trigger.sender][rnick]
    templist.append(action + new_phrase)
    search_dict[trigger.sender][rnick] = templist
    willie.memory['find_lines'] = search_dict

    # output
    if not me:
        new_phrase = '\x02meant\x02 to say: ' + new_phrase
    if trigger.group(1):
        phrase = '%s thinks %s %s' % (trigger.nick, rnick, new_phrase)
    else:
        phrase = '%s %s' % (trigger.nick, new_phrase)

    willie.say(phrase)

#Match nick, s/find/replace/flags. Flags and nick are optional, nick can be
#followed by comma or colon, anything after the first space after the third
#slash is ignored, you can escape slashes with backslashes, and if you want to
#search for an actual backslash followed by an actual slash, you're shit out of
#luck because this is the fucking regex of death as it is.
findandreplace.rule = r'(?:(\S+)[:,]\s+)?s/((?:\\/|[^/])+)/((?:\\/|[^/])*)(?:/(\S+))?'
findandreplace.priority = 'high'


