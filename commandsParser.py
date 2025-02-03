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
        4,1,9,71,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,6,
        2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,1,0,1,0,1,0,5,0,28,8,
        0,10,0,12,0,31,9,0,1,0,3,0,34,8,0,1,0,1,0,1,1,1,1,1,1,1,1,3,1,42,
        8,1,1,2,1,2,1,2,1,2,1,3,1,3,1,4,1,4,1,5,1,5,1,5,1,5,1,6,1,6,1,7,
        1,7,1,8,1,8,1,9,1,9,1,9,1,9,1,9,1,10,1,10,1,11,1,11,1,11,0,0,12,
        0,2,4,6,8,10,12,14,16,18,20,22,0,0,63,0,29,1,0,0,0,2,41,1,0,0,0,
        4,43,1,0,0,0,6,47,1,0,0,0,8,49,1,0,0,0,10,51,1,0,0,0,12,55,1,0,0,
        0,14,57,1,0,0,0,16,59,1,0,0,0,18,61,1,0,0,0,20,66,1,0,0,0,22,68,
        1,0,0,0,24,25,3,2,1,0,25,26,5,8,0,0,26,28,1,0,0,0,27,24,1,0,0,0,
        28,31,1,0,0,0,29,27,1,0,0,0,29,30,1,0,0,0,30,33,1,0,0,0,31,29,1,
        0,0,0,32,34,3,2,1,0,33,32,1,0,0,0,33,34,1,0,0,0,34,35,1,0,0,0,35,
        36,5,0,0,1,36,1,1,0,0,0,37,42,3,4,2,0,38,42,3,10,5,0,39,42,3,16,
        8,0,40,42,3,18,9,0,41,37,1,0,0,0,41,38,1,0,0,0,41,39,1,0,0,0,41,
        40,1,0,0,0,42,3,1,0,0,0,43,44,5,1,0,0,44,45,3,6,3,0,45,46,3,8,4,
        0,46,5,1,0,0,0,47,48,5,5,0,0,48,7,1,0,0,0,49,50,5,5,0,0,50,9,1,0,
        0,0,51,52,5,2,0,0,52,53,3,12,6,0,53,54,3,14,7,0,54,11,1,0,0,0,55,
        56,5,7,0,0,56,13,1,0,0,0,57,58,5,6,0,0,58,15,1,0,0,0,59,60,5,3,0,
        0,60,17,1,0,0,0,61,62,5,4,0,0,62,63,3,6,3,0,63,64,3,20,10,0,64,65,
        3,22,11,0,65,19,1,0,0,0,66,67,5,5,0,0,67,21,1,0,0,0,68,69,5,5,0,
        0,69,23,1,0,0,0,3,29,33,41
    ]

class commandsParser ( Parser ):

    grammarFileName = "commands.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'addvideo'", "'genmonth'", "'lintall'",
                     "'genvidmd'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>",
                      "<INVALID>", "STRING", "YEAR", "MONTH_DIGIT", "NEWLINE",
                      "WS" ]

    RULE_program = 0
    RULE_command = 1
    RULE_addVideo = 2
    RULE_videoId = 3
    RULE_videoName = 4
    RULE_genMonth = 5
    RULE_month = 6
    RULE_year = 7
    RULE_lintAll = 8
    RULE_genVidMD = 9
    RULE_caption = 10
    RULE_pathtoimg = 11

    ruleNames =  [ "program", "command", "addVideo", "videoId", "videoName",
                   "genMonth", "month", "year", "lintAll", "genVidMD", "caption",
                   "pathtoimg" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    STRING=5
    YEAR=6
    MONTH_DIGIT=7
    NEWLINE=8
    WS=9

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
            self.state = 29
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,0,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 24
                    self.command()
                    self.state = 25
                    self.match(commandsParser.NEWLINE)
                self.state = 31
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,0,self._ctx)

            self.state = 33
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 30) != 0):
                self.state = 32
                self.command()


            self.state = 35
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

        def addVideo(self):
            return self.getTypedRuleContext(commandsParser.AddVideoContext,0)


        def genMonth(self):
            return self.getTypedRuleContext(commandsParser.GenMonthContext,0)


        def lintAll(self):
            return self.getTypedRuleContext(commandsParser.LintAllContext,0)


        def genVidMD(self):
            return self.getTypedRuleContext(commandsParser.GenVidMDContext,0)


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
            self.state = 41
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [1]:
                self.enterOuterAlt(localctx, 1)
                self.state = 37
                self.addVideo()
                pass
            elif token in [2]:
                self.enterOuterAlt(localctx, 2)
                self.state = 38
                self.genMonth()
                pass
            elif token in [3]:
                self.enterOuterAlt(localctx, 3)
                self.state = 39
                self.lintAll()
                pass
            elif token in [4]:
                self.enterOuterAlt(localctx, 4)
                self.state = 40
                self.genVidMD()
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


    class AddVideoContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def videoId(self):
            return self.getTypedRuleContext(commandsParser.VideoIdContext,0)


        def videoName(self):
            return self.getTypedRuleContext(commandsParser.VideoNameContext,0)


        def getRuleIndex(self):
            return commandsParser.RULE_addVideo

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAddVideo" ):
                listener.enterAddVideo(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAddVideo" ):
                listener.exitAddVideo(self)




    def addVideo(self):

        localctx = commandsParser.AddVideoContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_addVideo)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 43
            self.match(commandsParser.T__0)
            self.state = 44
            self.videoId()
            self.state = 45
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
            self.state = 47
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
            self.state = 49
            self.match(commandsParser.STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class GenMonthContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def month(self):
            return self.getTypedRuleContext(commandsParser.MonthContext,0)


        def year(self):
            return self.getTypedRuleContext(commandsParser.YearContext,0)


        def getRuleIndex(self):
            return commandsParser.RULE_genMonth

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGenMonth" ):
                listener.enterGenMonth(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGenMonth" ):
                listener.exitGenMonth(self)




    def genMonth(self):

        localctx = commandsParser.GenMonthContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_genMonth)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 51
            self.match(commandsParser.T__1)
            self.state = 52
            self.month()
            self.state = 53
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
            self.state = 55
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
            self.state = 57
            self.match(commandsParser.YEAR)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LintAllContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return commandsParser.RULE_lintAll

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLintAll" ):
                listener.enterLintAll(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLintAll" ):
                listener.exitLintAll(self)




    def lintAll(self):

        localctx = commandsParser.LintAllContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_lintAll)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 59
            self.match(commandsParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class GenVidMDContext(ParserRuleContext):
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
            return commandsParser.RULE_genVidMD

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGenVidMD" ):
                listener.enterGenVidMD(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGenVidMD" ):
                listener.exitGenVidMD(self)




    def genVidMD(self):

        localctx = commandsParser.GenVidMDContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_genVidMD)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 61
            self.match(commandsParser.T__3)
            self.state = 62
            self.videoId()
            self.state = 63
            self.caption()
            self.state = 64
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
        self.enterRule(localctx, 20, self.RULE_caption)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 66
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
        self.enterRule(localctx, 22, self.RULE_pathtoimg)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 68
            self.match(commandsParser.STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx
