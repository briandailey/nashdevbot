"""
twitter_handle.py - Willie Twitter Handle Preference Module
Copyright 2013, William Golden, codebomber.com

http://willie.dftba.net
"""

import re
from willie.tools import Nick


def setup(willie):
    if willie.db and not willie.db.preferences.has_columns('twitter_handle'):
        # add a twitter_handle column if does not exists on preferences table
        willie.db.preferences.add_columns(['twitter_handle'])


def handle(willie, trigger):
    """
    Associates your IRC nick with a Twitter handle. Example: .handle @egdelwonk
    """

    # prevent blocked users from accessing the trigger
    if trigger.nick in willie.config.core.nick_blocks:
        return

    nick_target = trigger.group(2)
    handle_match_re = re.compile(r'@([A-Za-z0-9_]+)')
    updated_handle = re.findall(handle_match_re, trigger)

    if willie.db and updated_handle:
        # update the triggering nickname's twitter handle
        willie.db.preferences.update(Nick(trigger.nick), {
            'twitter_handle': updated_handle[0]})
        willie.say(
            Nick(trigger.nick) + ': your twitter handle is now @' + updated_handle[0])

    elif nick_target:
        # establish nick target
        nick_target = Nick(nick_target.strip())

        # return saved handle
        nick_handle = get_handle(willie, nick_target)

        # targeted nickname has a saved twitter handle
        if nick_handle:
            willie.say(
                Nick(trigger.nick) + ': ' + nick_target +
                '\'s twitter handle is: @' + nick_handle
                + ' / http://twitter.com/' + nick_handle)

        # targeted nickname does not exists in usersdb preferences
        else:
            willie.say(
                Nick(trigger.nick) + ': ' + nick_target + ' does not have a twitter handle saved yet.')

    # no additional message was passed to the trigger
    else:
        nick_handle = get_handle(willie, Nick(trigger.nick))
        if nick_handle:
            willie.say(Nick(trigger.nick) + ': ' +
                       'your twitter handle is @' + nick_handle)
        else:
            willie.say(Nick(
                trigger.nick) + ': ' + 'your twitter handle has not been saved yet.')


def get_handle(willie, nick):
    """
    Find a users twitter handle by nickname saved in user preferences.
    """
    # check if the nickname has any saved preferences
    if willie.db and nick in willie.db.preferences:
        return willie.db.preferences.get(nick, 'twitter_handle')

    return


if __name__ == "__main__":
    print __doc__.strip()

# register the triggers and priority for the handle function
handle.commands = ['handle']
handle.priority = 'medium'
