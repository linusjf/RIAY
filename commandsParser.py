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
        4,1,10,59,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,1,0,1,0,1,0,1,0,3,0,27,8,0,1,
        1,1,1,1,1,1,1,1,2,1,2,1,3,1,3,1,4,1,4,1,4,1,4,1,5,1,5,1,6,1,6,1,
        6,1,6,1,6,1,7,1,7,1,8,1,8,1,8,1,8,1,8,1,9,1,9,1,10,1,10,1,10,0,0,
        11,0,2,4,6,8,10,12,14,16,18,20,0,0,50,0,26,1,0,0,0,2,28,1,0,0,0,
        4,32,1,0,0,0,6,34,1,0,0,0,8,36,1,0,0,0,10,40,1,0,0,0,12,42,1,0,0,
        0,14,47,1,0,0,0,16,49,1,0,0,0,18,54,1,0,0,0,20,56,1,0,0,0,22,27,
        3,2,1,0,23,27,3,8,4,0,24,27,3,14,7,0,25,27,3,16,8,0,26,22,1,0,0,
        0,26,23,1,0,0,0,26,24,1,0,0,0,26,25,1,0,0,0,27,1,1,0,0,0,28,29,5,
        1,0,0,29,30,3,4,2,0,30,31,3,6,3,0,31,3,1,0,0,0,32,33,5,6,0,0,33,
        5,1,0,0,0,34,35,5,6,0,0,35,7,1,0,0,0,36,37,5,2,0,0,37,38,3,10,5,
        0,38,39,3,12,6,0,39,9,1,0,0,0,40,41,5,7,0,0,41,11,1,0,0,0,42,43,
        5,8,0,0,43,44,5,8,0,0,44,45,5,8,0,0,45,46,5,8,0,0,46,13,1,0,0,0,
        47,48,5,3,0,0,48,15,1,0,0,0,49,50,5,4,0,0,50,51,3,4,2,0,51,52,3,
        18,9,0,52,53,3,20,10,0,53,17,1,0,0,0,54,55,5,6,0,0,55,19,1,0,0,0,
        56,57,5,6,0,0,57,21,1,0,0,0,1,26
    ]

class commandsParser ( Parser ):

    grammarFileName = "commands.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'addvideo'", "'genmonth'", "'lintall'",
                     "'genvidmd'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>",
                      "<INVALID>", "COMMENT", "STRING", "MONTH_DIGIT", "DIGIT",
                      "INTEGER", "WS" ]

    RULE_program = 0
    RULE_addVideo = 1
    RULE_videoId = 2
    RULE_videoName = 3
    RULE_genMonth = 4
    RULE_month = 5
    RULE_year = 6
    RULE_lintAll = 7
    RULE_genVidMD = 8
    RULE_caption = 9
    RULE_pathtoimg = 10

    ruleNames =  [ "program", "addVideo", "videoId", "videoName", "genMonth",
                   "month", "year", "lintAll", "genVidMD", "caption", "pathtoimg" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    COMMENT=5
    STRING=6
    MONTH_DIGIT=7
    DIGIT=8
    INTEGER=9
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

        def addVideo(self):
            return self.getTypedRuleContext(commandsParser.AddVideoContext,0)


        def genMonth(self):
            return self.getTypedRuleContext(commandsParser.GenMonthContext,0)


        def lintAll(self):
            return self.getTypedRuleContext(commandsParser.LintAllContext,0)


        def genVidMD(self):
            return self.getTypedRuleContext(commandsParser.GenVidMDContext,0)


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
        try:
            self.state = 26
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [1]:
                self.enterOuterAlt(localctx, 1)
                self.state = 22
                self.addVideo()
                pass
            elif token in [2]:
                self.enterOuterAlt(localctx, 2)
                self.state = 23
                self.genMonth()
                pass
            elif token in [3]:
                self.enterOuterAlt(localctx, 3)
                self.state = 24
                self.lintAll()
                pass
            elif token in [4]:
                self.enterOuterAlt(localctx, 4)
                self.state = 25
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
        self.enterRule(localctx, 2, self.RULE_addVideo)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 28
            self.match(commandsParser.T__0)
            self.state = 29
            self.videoId()
            self.state = 30
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
        self.enterRule(localctx, 4, self.RULE_videoId)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 32
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
        self.enterRule(localctx, 6, self.RULE_videoName)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 34
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
        self.enterRule(localctx, 8, self.RULE_genMonth)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 36
            self.match(commandsParser.T__1)
            self.state = 37
            self.month()
            self.state = 38
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
        self.enterRule(localctx, 10, self.RULE_month)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 40
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

        def DIGIT(self, i:int=None):
            if i is None:
                return self.getTokens(commandsParser.DIGIT)
            else:
                return self.getToken(commandsParser.DIGIT, i)

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
        self.enterRule(localctx, 12, self.RULE_year)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 42
            self.match(commandsParser.DIGIT)
            self.state = 43
            self.match(commandsParser.DIGIT)
            self.state = 44
            self.match(commandsParser.DIGIT)
            self.state = 45
            self.match(commandsParser.DIGIT)
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
        self.enterRule(localctx, 14, self.RULE_lintAll)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 47
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
        self.enterRule(localctx, 16, self.RULE_genVidMD)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 49
            self.match(commandsParser.T__3)
            self.state = 50
            self.videoId()
            self.state = 51
            self.caption()
            self.state = 52
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
        self.enterRule(localctx, 18, self.RULE_caption)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 54
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
        self.enterRule(localctx, 20, self.RULE_pathtoimg)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 56
            self.match(commandsParser.STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx
