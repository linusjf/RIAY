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
        4,1,10,77,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,1,0,1,0,
        1,0,1,0,5,0,31,8,0,10,0,12,0,34,9,0,1,0,3,0,37,8,0,1,0,1,0,1,1,1,
        1,1,1,1,1,1,1,3,1,46,8,1,1,2,1,2,1,2,1,2,1,3,1,3,1,4,1,4,1,5,1,5,
        1,5,1,5,1,6,1,6,1,7,1,7,1,8,1,8,1,9,1,9,1,10,1,10,1,10,1,10,1,10,
        1,11,1,11,1,12,1,12,1,12,0,0,13,0,2,4,6,8,10,12,14,16,18,20,22,24,
        0,0,70,0,32,1,0,0,0,2,45,1,0,0,0,4,47,1,0,0,0,6,51,1,0,0,0,8,53,
        1,0,0,0,10,55,1,0,0,0,12,59,1,0,0,0,14,61,1,0,0,0,16,63,1,0,0,0,
        18,65,1,0,0,0,20,67,1,0,0,0,22,72,1,0,0,0,24,74,1,0,0,0,26,27,3,
        2,1,0,27,28,5,9,0,0,28,31,1,0,0,0,29,31,5,9,0,0,30,26,1,0,0,0,30,
        29,1,0,0,0,31,34,1,0,0,0,32,30,1,0,0,0,32,33,1,0,0,0,33,36,1,0,0,
        0,34,32,1,0,0,0,35,37,3,2,1,0,36,35,1,0,0,0,36,37,1,0,0,0,37,38,
        1,0,0,0,38,39,5,0,0,1,39,1,1,0,0,0,40,46,3,4,2,0,41,46,3,10,5,0,
        42,46,3,16,8,0,43,46,3,20,10,0,44,46,3,18,9,0,45,40,1,0,0,0,45,41,
        1,0,0,0,45,42,1,0,0,0,45,43,1,0,0,0,45,44,1,0,0,0,46,3,1,0,0,0,47,
        48,5,1,0,0,48,49,3,6,3,0,49,50,3,8,4,0,50,5,1,0,0,0,51,52,5,6,0,
        0,52,7,1,0,0,0,53,54,5,6,0,0,54,9,1,0,0,0,55,56,5,2,0,0,56,57,3,
        12,6,0,57,58,3,14,7,0,58,11,1,0,0,0,59,60,5,8,0,0,60,13,1,0,0,0,
        61,62,5,7,0,0,62,15,1,0,0,0,63,64,5,3,0,0,64,17,1,0,0,0,65,66,5,
        4,0,0,66,19,1,0,0,0,67,68,5,5,0,0,68,69,3,6,3,0,69,70,3,22,11,0,
        70,71,3,24,12,0,71,21,1,0,0,0,72,73,5,6,0,0,73,23,1,0,0,0,74,75,
        5,6,0,0,75,25,1,0,0,0,4,30,32,36,45
    ]

class commandsParser ( Parser ):

    grammarFileName = "commands.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'addvideo'", "'genmonth'", "'lintall'",
                     "'stitch'", "'genvidmd'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>",
                      "<INVALID>", "<INVALID>", "STRING", "YEAR", "MONTH_DIGIT",
                      "NEWLINE", "WS" ]

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
    RULE_genvidmd = 10
    RULE_caption = 11
    RULE_pathtoimg = 12

    ruleNames =  [ "program", "command", "addvideo", "videoId", "videoName",
                   "genmonth", "month", "year", "lintall", "stitch", "genvidmd",
                   "caption", "pathtoimg" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    STRING=6
    YEAR=7
    MONTH_DIGIT=8
    NEWLINE=9
    WS=10

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
            self.state = 32
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,1,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 30
                    self._errHandler.sync(self)
                    token = self._input.LA(1)
                    if token in [1, 2, 3, 4, 5]:
                        self.state = 26
                        self.command()
                        self.state = 27
                        self.match(commandsParser.NEWLINE)
                        pass
                    elif token in [9]:
                        self.state = 29
                        self.match(commandsParser.NEWLINE)
                        pass
                    else:
                        raise NoViableAltException(self)

                self.state = 34
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

            self.state = 36
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 62) != 0):
                self.state = 35
                self.command()


            self.state = 38
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


        def genvidmd(self):
            return self.getTypedRuleContext(commandsParser.GenvidmdContext,0)


        def stitch(self):
            return self.getTypedRuleContext(commandsParser.StitchContext,0)


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
            self.state = 45
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [1]:
                self.enterOuterAlt(localctx, 1)
                self.state = 40
                self.addvideo()
                pass
            elif token in [2]:
                self.enterOuterAlt(localctx, 2)
                self.state = 41
                self.genmonth()
                pass
            elif token in [3]:
                self.enterOuterAlt(localctx, 3)
                self.state = 42
                self.lintall()
                pass
            elif token in [5]:
                self.enterOuterAlt(localctx, 4)
                self.state = 43
                self.genvidmd()
                pass
            elif token in [4]:
                self.enterOuterAlt(localctx, 5)
                self.state = 44
                self.stitch()
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
            self.state = 47
            self.match(commandsParser.T__0)
            self.state = 48
            self.videoId()
            self.state = 49
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
            self.state = 51
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
            self.state = 53
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
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 55
            self.match(commandsParser.T__1)
            self.state = 56
            self.month()
            self.state = 57
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

        def MONTH_DIGIT(self):
            return self.getToken(commandsParser.MONTH_DIGIT, 0)

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
            self.state = 59
            self.match(commandsParser.MONTH_DIGIT)
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
            self.state = 61
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
            self.state = 63
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
            self.state = 65
            self.match(commandsParser.T__3)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class GenvidmdContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def videoId(self):
            return self.getTypedRuleContext(commandsParser.VideoIdContext,0)


        def caption(self):
            return self.getTypedRuleContext(commandsParser.CaptionContext,0)


        def pathtoimg(self):
            return self.getTypedRuleContext(commandsParser.PathtoimgContext,0)


        def getRuleIndex(self):
            return commandsParser.RULE_genvidmd

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGenvidmd" ):
                listener.enterGenvidmd(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGenvidmd" ):
                listener.exitGenvidmd(self)




    def genvidmd(self):

        localctx = commandsParser.GenvidmdContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_genvidmd)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 67
            self.match(commandsParser.T__4)
            self.state = 68
            self.videoId()
            self.state = 69
            self.caption()
            self.state = 70
            self.pathtoimg()
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
        self.enterRule(localctx, 22, self.RULE_caption)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 72
            self.match(commandsParser.STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PathtoimgContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(commandsParser.STRING, 0)

        def getRuleIndex(self):
            return commandsParser.RULE_pathtoimg

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPathtoimg" ):
                listener.enterPathtoimg(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPathtoimg" ):
                listener.exitPathtoimg(self)




    def pathtoimg(self):

        localctx = commandsParser.PathtoimgContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_pathtoimg)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 74
            self.match(commandsParser.STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx
