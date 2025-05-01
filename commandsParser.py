# Generated from commands.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,14,99,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,1,0,1,0,1,0,1,0,5,0,39,8,0,10,0,12,
        0,42,9,0,1,0,3,0,45,8,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,
        56,8,1,1,2,1,2,1,2,1,2,1,3,1,3,1,4,1,4,1,5,1,5,1,5,3,5,69,8,5,1,
        6,1,6,1,7,1,7,1,8,1,8,1,9,1,9,1,10,1,10,1,10,1,11,1,11,1,12,1,12,
        1,12,1,12,1,13,1,13,1,14,1,14,1,14,1,14,1,14,1,15,1,15,1,16,1,16,
        1,16,0,0,17,0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,0,0,91,
        0,40,1,0,0,0,2,55,1,0,0,0,4,57,1,0,0,0,6,61,1,0,0,0,8,63,1,0,0,0,
        10,65,1,0,0,0,12,70,1,0,0,0,14,72,1,0,0,0,16,74,1,0,0,0,18,76,1,
        0,0,0,20,78,1,0,0,0,22,81,1,0,0,0,24,83,1,0,0,0,26,87,1,0,0,0,28,
        89,1,0,0,0,30,94,1,0,0,0,32,96,1,0,0,0,34,35,3,2,1,0,35,36,5,12,
        0,0,36,39,1,0,0,0,37,39,5,12,0,0,38,34,1,0,0,0,38,37,1,0,0,0,39,
        42,1,0,0,0,40,38,1,0,0,0,40,41,1,0,0,0,41,44,1,0,0,0,42,40,1,0,0,
        0,43,45,3,2,1,0,44,43,1,0,0,0,44,45,1,0,0,0,45,46,1,0,0,0,46,47,
        5,0,0,1,47,1,1,0,0,0,48,56,3,4,2,0,49,56,3,10,5,0,50,56,3,16,8,0,
        51,56,3,18,9,0,52,56,3,20,10,0,53,56,3,24,12,0,54,56,3,28,14,0,55,
        48,1,0,0,0,55,49,1,0,0,0,55,50,1,0,0,0,55,51,1,0,0,0,55,52,1,0,0,
        0,55,53,1,0,0,0,55,54,1,0,0,0,56,3,1,0,0,0,57,58,5,1,0,0,58,59,3,
        6,3,0,59,60,3,8,4,0,60,5,1,0,0,0,61,62,5,8,0,0,62,7,1,0,0,0,63,64,
        5,8,0,0,64,9,1,0,0,0,65,66,5,2,0,0,66,68,3,12,6,0,67,69,3,14,7,0,
        68,67,1,0,0,0,68,69,1,0,0,0,69,11,1,0,0,0,70,71,5,10,0,0,71,13,1,
        0,0,0,72,73,5,9,0,0,73,15,1,0,0,0,74,75,5,3,0,0,75,17,1,0,0,0,76,
        77,5,4,0,0,77,19,1,0,0,0,78,79,5,5,0,0,79,80,3,22,11,0,80,21,1,0,
        0,0,81,82,5,8,0,0,82,23,1,0,0,0,83,84,5,6,0,0,84,85,3,6,3,0,85,86,
        3,26,13,0,86,25,1,0,0,0,87,88,5,11,0,0,88,27,1,0,0,0,89,90,5,7,0,
        0,90,91,3,30,15,0,91,92,3,32,16,0,92,93,3,26,13,0,93,29,1,0,0,0,
        94,95,5,8,0,0,95,31,1,0,0,0,96,97,5,8,0,0,97,33,1,0,0,0,5,38,40,
        44,55,68
    ]

class commandsParser ( Parser ):

    grammarFileName = "commands.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'addvideo'", "'genmonth'", "'lintall'", 
                     "'stitch'", "'gentoc'", "'addvideotoday'", "'addimgtoday'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "STRING", "YEAR", "MONTH", "DAY_NUMBER", "NEWLINE", 
                      "WS", "ANY" ]

    RULE_program = 0
    RULE_command = 1
    RULE_addvideo = 2
    RULE_videoId = 3
    RULE_videoName = 4
    RULE_genmonth = 5
    RULE_month = 6
    RULE_year = 7
    RULE_lintall = 8
    RULE_stitch = 9
    RULE_gentoc = 10
    RULE_pathtomdfile = 11
    RULE_addvideotoday = 12
    RULE_dayofyear = 13
    RULE_addimgtoday = 14
    RULE_imagepath = 15
    RULE_caption = 16

    ruleNames =  [ "program", "command", "addvideo", "videoId", "videoName", 
                   "genmonth", "month", "year", "lintall", "stitch", "gentoc", 
                   "pathtomdfile", "addvideotoday", "dayofyear", "addimgtoday", 
                   "imagepath", "caption" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    STRING=8
    YEAR=9
    MONTH=10
    DAY_NUMBER=11
    NEWLINE=12
    WS=13
    ANY=14

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgramContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(commandsParser.EOF, 0)

        def command(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(commandsParser.CommandContext)
            else:
                return self.getTypedRuleContext(commandsParser.CommandContext,i)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(commandsParser.NEWLINE)
            else:
                return self.getToken(commandsParser.NEWLINE, i)

        def getRuleIndex(self):
            return commandsParser.RULE_program

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProgram" ):
                listener.enterProgram(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProgram" ):
                listener.exitProgram(self)




    def program(self):

        localctx = commandsParser.ProgramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_program)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 40
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,1,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 38
                    self._errHandler.sync(self)
                    token = self._input.LA(1)
                    if token in [1, 2, 3, 4, 5, 6, 7]:
                        self.state = 34
                        self.command()
                        self.state = 35
                        self.match(commandsParser.NEWLINE)
                        pass
                    elif token in [12]:
                        self.state = 37
                        self.match(commandsParser.NEWLINE)
                        pass
                    else:
                        raise NoViableAltException(self)
             
                self.state = 42
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

            self.state = 44
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 254) != 0):
                self.state = 43
                self.command()


            self.state = 46
            self.match(commandsParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CommandContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def addvideo(self):
            return self.getTypedRuleContext(commandsParser.AddvideoContext,0)


        def genmonth(self):
            return self.getTypedRuleContext(commandsParser.GenmonthContext,0)


        def lintall(self):
            return self.getTypedRuleContext(commandsParser.LintallContext,0)


        def stitch(self):
            return self.getTypedRuleContext(commandsParser.StitchContext,0)


        def gentoc(self):
            return self.getTypedRuleContext(commandsParser.GentocContext,0)


        def addvideotoday(self):
            return self.getTypedRuleContext(commandsParser.AddvideotodayContext,0)


        def addimgtoday(self):
            return self.getTypedRuleContext(commandsParser.AddimgtodayContext,0)


        def getRuleIndex(self):
            return commandsParser.RULE_command

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCommand" ):
                listener.enterCommand(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCommand" ):
                listener.exitCommand(self)




    def command(self):

        localctx = commandsParser.CommandContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_command)
        try:
            self.state = 55
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [1]:
                self.enterOuterAlt(localctx, 1)
                self.state = 48
                self.addvideo()
                pass
            elif token in [2]:
                self.enterOuterAlt(localctx, 2)
                self.state = 49
                self.genmonth()
                pass
            elif token in [3]:
                self.enterOuterAlt(localctx, 3)
                self.state = 50
                self.lintall()
                pass
            elif token in [4]:
                self.enterOuterAlt(localctx, 4)
                self.state = 51
                self.stitch()
                pass
            elif token in [5]:
                self.enterOuterAlt(localctx, 5)
                self.state = 52
                self.gentoc()
                pass
            elif token in [6]:
                self.enterOuterAlt(localctx, 6)
                self.state = 53
                self.addvideotoday()
                pass
            elif token in [7]:
                self.enterOuterAlt(localctx, 7)
                self.state = 54
                self.addimgtoday()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AddvideoContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def videoId(self):
            return self.getTypedRuleContext(commandsParser.VideoIdContext,0)


        def videoName(self):
            return self.getTypedRuleContext(commandsParser.VideoNameContext,0)


        def getRuleIndex(self):
            return commandsParser.RULE_addvideo

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAddvideo" ):
                listener.enterAddvideo(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAddvideo" ):
                listener.exitAddvideo(self)




    def addvideo(self):

        localctx = commandsParser.AddvideoContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_addvideo)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 57
            self.match(commandsParser.T__0)
            self.state = 58
            self.videoId()
            self.state = 59
            self.videoName()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class VideoIdContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(commandsParser.STRING, 0)

        def getRuleIndex(self):
            return commandsParser.RULE_videoId

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVideoId" ):
                listener.enterVideoId(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVideoId" ):
                listener.exitVideoId(self)




    def videoId(self):

        localctx = commandsParser.VideoIdContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_videoId)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 61
            self.match(commandsParser.STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class VideoNameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(commandsParser.STRING, 0)

        def getRuleIndex(self):
            return commandsParser.RULE_videoName

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVideoName" ):
                listener.enterVideoName(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVideoName" ):
                listener.exitVideoName(self)




    def videoName(self):

        localctx = commandsParser.VideoNameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_videoName)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 63
            self.match(commandsParser.STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class GenmonthContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def month(self):
            return self.getTypedRuleContext(commandsParser.MonthContext,0)


        def year(self):
            return self.getTypedRuleContext(commandsParser.YearContext,0)


        def getRuleIndex(self):
            return commandsParser.RULE_genmonth

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGenmonth" ):
                listener.enterGenmonth(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGenmonth" ):
                listener.exitGenmonth(self)




    def genmonth(self):

        localctx = commandsParser.GenmonthContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_genmonth)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 65
            self.match(commandsParser.T__1)
            self.state = 66
            self.month()
            self.state = 68
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==9:
                self.state = 67
                self.year()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MonthContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def MONTH(self):
            return self.getToken(commandsParser.MONTH, 0)

        def getRuleIndex(self):
            return commandsParser.RULE_month

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMonth" ):
                listener.enterMonth(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMonth" ):
                listener.exitMonth(self)




    def month(self):

        localctx = commandsParser.MonthContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_month)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 70
            self.match(commandsParser.MONTH)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class YearContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def YEAR(self):
            return self.getToken(commandsParser.YEAR, 0)

        def getRuleIndex(self):
            return commandsParser.RULE_year

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterYear" ):
                listener.enterYear(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitYear" ):
                listener.exitYear(self)




    def year(self):

        localctx = commandsParser.YearContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_year)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 72
            self.match(commandsParser.YEAR)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LintallContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return commandsParser.RULE_lintall

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLintall" ):
                listener.enterLintall(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLintall" ):
                listener.exitLintall(self)




    def lintall(self):

        localctx = commandsParser.LintallContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_lintall)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 74
            self.match(commandsParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StitchContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return commandsParser.RULE_stitch

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStitch" ):
                listener.enterStitch(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStitch" ):
                listener.exitStitch(self)




    def stitch(self):

        localctx = commandsParser.StitchContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_stitch)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 76
            self.match(commandsParser.T__3)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class GentocContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def pathtomdfile(self):
            return self.getTypedRuleContext(commandsParser.PathtomdfileContext,0)


        def getRuleIndex(self):
            return commandsParser.RULE_gentoc

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGentoc" ):
                listener.enterGentoc(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGentoc" ):
                listener.exitGentoc(self)




    def gentoc(self):

        localctx = commandsParser.GentocContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_gentoc)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 78
            self.match(commandsParser.T__4)
            self.state = 79
            self.pathtomdfile()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PathtomdfileContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(commandsParser.STRING, 0)

        def getRuleIndex(self):
            return commandsParser.RULE_pathtomdfile

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPathtomdfile" ):
                listener.enterPathtomdfile(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPathtomdfile" ):
                listener.exitPathtomdfile(self)




    def pathtomdfile(self):

        localctx = commandsParser.PathtomdfileContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_pathtomdfile)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 81
            self.match(commandsParser.STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AddvideotodayContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def videoId(self):
            return self.getTypedRuleContext(commandsParser.VideoIdContext,0)


        def dayofyear(self):
            return self.getTypedRuleContext(commandsParser.DayofyearContext,0)


        def getRuleIndex(self):
            return commandsParser.RULE_addvideotoday

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAddvideotoday" ):
                listener.enterAddvideotoday(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAddvideotoday" ):
                listener.exitAddvideotoday(self)




    def addvideotoday(self):

        localctx = commandsParser.AddvideotodayContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_addvideotoday)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 83
            self.match(commandsParser.T__5)
            self.state = 84
            self.videoId()
            self.state = 85
            self.dayofyear()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DayofyearContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DAY_NUMBER(self):
            return self.getToken(commandsParser.DAY_NUMBER, 0)

        def getRuleIndex(self):
            return commandsParser.RULE_dayofyear

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDayofyear" ):
                listener.enterDayofyear(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDayofyear" ):
                listener.exitDayofyear(self)




    def dayofyear(self):

        localctx = commandsParser.DayofyearContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_dayofyear)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 87
            self.match(commandsParser.DAY_NUMBER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AddimgtodayContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def imagepath(self):
            return self.getTypedRuleContext(commandsParser.ImagepathContext,0)


        def caption(self):
            return self.getTypedRuleContext(commandsParser.CaptionContext,0)


        def dayofyear(self):
            return self.getTypedRuleContext(commandsParser.DayofyearContext,0)


        def getRuleIndex(self):
            return commandsParser.RULE_addimgtoday

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAddimgtoday" ):
                listener.enterAddimgtoday(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAddimgtoday" ):
                listener.exitAddimgtoday(self)




    def addimgtoday(self):

        localctx = commandsParser.AddimgtodayContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_addimgtoday)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 89
            self.match(commandsParser.T__6)
            self.state = 90
            self.imagepath()
            self.state = 91
            self.caption()
            self.state = 92
            self.dayofyear()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ImagepathContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(commandsParser.STRING, 0)

        def getRuleIndex(self):
            return commandsParser.RULE_imagepath

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterImagepath" ):
                listener.enterImagepath(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitImagepath" ):
                listener.exitImagepath(self)




    def imagepath(self):

        localctx = commandsParser.ImagepathContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_imagepath)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 94
            self.match(commandsParser.STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CaptionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(commandsParser.STRING, 0)

        def getRuleIndex(self):
            return commandsParser.RULE_caption

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCaption" ):
                listener.enterCaption(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCaption" ):
                listener.exitCaption(self)




    def caption(self):

        localctx = commandsParser.CaptionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_caption)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 96
            self.match(commandsParser.STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





