import re

class ReEvent:
    DOCTEST_INPUT_A = r'player5_changeCard'
    RE = re.compile(r'^player(?P<player>\d)_(?P<event>.*)$')

    def __init__(self, match):
        d = match.groupdict()
        self.player = d['player']
        self.event = d['event']

    @classmethod
    def search(cls, test_string):
        '''
        >>> result = ReEvent.search(ReEvent.DOCTEST_INPUT_A)
        >>> result.player
        '5'
        >>> result.event
        'changeCard'
        '''
        match = ReEvent.RE.search(test_string)
        if match is None:
            return None
        return ReEvent(match)

import doctest
doctest.testmod()
# TODO: Throw exception
