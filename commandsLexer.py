# Generated from commands.g4 by ANTLR 4.13.2
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO


def serializedATN():
    return [
        4,0,9,103,6,-1,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,
        6,7,6,2,7,7,7,2,8,7,8,2,9,7,9,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,
        0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,2,1,2,1,2,1,2,1,2,1,
        2,1,2,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,4,1,4,5,4,59,8,4,10,
        4,12,4,62,9,4,1,4,1,4,1,5,1,5,1,5,1,5,1,5,1,6,1,6,1,6,1,6,1,6,3,
        6,76,8,6,1,7,3,7,79,8,7,1,7,1,7,1,8,4,8,84,8,8,11,8,12,8,85,1,8,
        1,8,1,9,1,9,5,9,92,8,9,10,9,12,9,95,9,9,1,9,3,9,98,8,9,1,9,1,9,1,
        9,1,9,1,60,0,10,1,1,3,2,5,3,7,4,9,5,11,6,13,7,15,8,17,9,19,0,1,0,
        4,1,0,50,50,1,0,48,57,3,0,9,10,13,13,32,32,2,0,10,10,13,13,109,0,
        1,1,0,0,0,0,3,1,0,0,0,0,5,1,0,0,0,0,7,1,0,0,0,0,9,1,0,0,0,0,11,1,
        0,0,0,0,13,1,0,0,0,0,15,1,0,0,0,0,17,1,0,0,0,0,19,1,0,0,0,1,21,1,
        0,0,0,3,30,1,0,0,0,5,39,1,0,0,0,7,47,1,0,0,0,9,56,1,0,0,0,11,65,
        1,0,0,0,13,75,1,0,0,0,15,78,1,0,0,0,17,83,1,0,0,0,19,89,1,0,0,0,
        21,22,5,97,0,0,22,23,5,100,0,0,23,24,5,100,0,0,24,25,5,118,0,0,25,
        26,5,105,0,0,26,27,5,100,0,0,27,28,5,101,0,0,28,29,5,111,0,0,29,
        2,1,0,0,0,30,31,5,103,0,0,31,32,5,101,0,0,32,33,5,110,0,0,33,34,
        5,109,0,0,34,35,5,111,0,0,35,36,5,110,0,0,36,37,5,116,0,0,37,38,
        5,104,0,0,38,4,1,0,0,0,39,40,5,108,0,0,40,41,5,105,0,0,41,42,5,110,
        0,0,42,43,5,116,0,0,43,44,5,97,0,0,44,45,5,108,0,0,45,46,5,108,0,
        0,46,6,1,0,0,0,47,48,5,103,0,0,48,49,5,101,0,0,49,50,5,110,0,0,50,
        51,5,118,0,0,51,52,5,105,0,0,52,53,5,100,0,0,53,54,5,109,0,0,54,
        55,5,100,0,0,55,8,1,0,0,0,56,60,5,34,0,0,57,59,9,0,0,0,58,57,1,0,
        0,0,59,62,1,0,0,0,60,61,1,0,0,0,60,58,1,0,0,0,61,63,1,0,0,0,62,60,
        1,0,0,0,63,64,5,34,0,0,64,10,1,0,0,0,65,66,7,0,0,0,66,67,7,1,0,0,
        67,68,7,1,0,0,68,69,7,1,0,0,69,12,1,0,0,0,70,71,5,49,0,0,71,76,2,
        48,50,0,72,73,5,48,0,0,73,76,2,49,57,0,74,76,2,49,57,0,75,70,1,0,
        0,0,75,72,1,0,0,0,75,74,1,0,0,0,76,14,1,0,0,0,77,79,5,13,0,0,78,
        77,1,0,0,0,78,79,1,0,0,0,79,80,1,0,0,0,80,81,5,10,0,0,81,16,1,0,
        0,0,82,84,7,2,0,0,83,82,1,0,0,0,84,85,1,0,0,0,85,83,1,0,0,0,85,86,
        1,0,0,0,86,87,1,0,0,0,87,88,6,8,0,0,88,18,1,0,0,0,89,93,5,35,0,0,
        90,92,8,3,0,0,91,90,1,0,0,0,92,95,1,0,0,0,93,91,1,0,0,0,93,94,1,
        0,0,0,94,97,1,0,0,0,95,93,1,0,0,0,96,98,5,13,0,0,97,96,1,0,0,0,97,
        98,1,0,0,0,98,99,1,0,0,0,99,100,5,10,0,0,100,101,1,0,0,0,101,102,
        6,9,1,0,102,20,1,0,0,0,7,0,60,75,78,85,93,97,2,6,0,0,7,8,0
    ]

class commandsLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    T__0 = 1
    T__1 = 2
    T__2 = 3
    T__3 = 4
    STRING = 5
    YEAR = 6
    MONTH_DIGIT = 7
    NEWLINE = 8
    WS = 9

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'addvideo'", "'genmonth'", "'lintall'", "'genvidmd'" ]

    symbolicNames = [ "<INVALID>",
            "STRING", "YEAR", "MONTH_DIGIT", "NEWLINE", "WS" ]

    ruleNames = [ "T__0", "T__1", "T__2", "T__3", "STRING", "YEAR", "MONTH_DIGIT",
                  "NEWLINE", "WS", "COMMENT" ]

    grammarFileName = "commands.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None
