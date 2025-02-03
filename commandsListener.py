# Generated from commands.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .commandsParser import commandsParser
else:
    from commandsParser import commandsParser

# This class defines a complete listener for a parse tree produced by commandsParser.
class commandsListener(ParseTreeListener):

    # Enter a parse tree produced by commandsParser#program.
    def enterProgram(self, ctx:commandsParser.ProgramContext):
        pass

    # Exit a parse tree produced by commandsParser#program.
    def exitProgram(self, ctx:commandsParser.ProgramContext):
        pass


    # Enter a parse tree produced by commandsParser#addVideo.
    def enterAddVideo(self, ctx:commandsParser.AddVideoContext):
        pass

    # Exit a parse tree produced by commandsParser#addVideo.
    def exitAddVideo(self, ctx:commandsParser.AddVideoContext):
        pass


    # Enter a parse tree produced by commandsParser#videoId.
    def enterVideoId(self, ctx:commandsParser.VideoIdContext):
        pass

    # Exit a parse tree produced by commandsParser#videoId.
    def exitVideoId(self, ctx:commandsParser.VideoIdContext):
        pass


    # Enter a parse tree produced by commandsParser#videoName.
    def enterVideoName(self, ctx:commandsParser.VideoNameContext):
        pass

    # Exit a parse tree produced by commandsParser#videoName.
    def exitVideoName(self, ctx:commandsParser.VideoNameContext):
        pass


    # Enter a parse tree produced by commandsParser#genMonth.
    def enterGenMonth(self, ctx:commandsParser.GenMonthContext):
        pass

    # Exit a parse tree produced by commandsParser#genMonth.
    def exitGenMonth(self, ctx:commandsParser.GenMonthContext):
        pass


    # Enter a parse tree produced by commandsParser#month.
    def enterMonth(self, ctx:commandsParser.MonthContext):
        pass

    # Exit a parse tree produced by commandsParser#month.
    def exitMonth(self, ctx:commandsParser.MonthContext):
        pass


    # Enter a parse tree produced by commandsParser#year.
    def enterYear(self, ctx:commandsParser.YearContext):
        pass

    # Exit a parse tree produced by commandsParser#year.
    def exitYear(self, ctx:commandsParser.YearContext):
        pass


    # Enter a parse tree produced by commandsParser#lintAll.
    def enterLintAll(self, ctx:commandsParser.LintAllContext):
        pass

    # Exit a parse tree produced by commandsParser#lintAll.
    def exitLintAll(self, ctx:commandsParser.LintAllContext):
        pass


    # Enter a parse tree produced by commandsParser#genVidMD.
    def enterGenVidMD(self, ctx:commandsParser.GenVidMDContext):
        pass

    # Exit a parse tree produced by commandsParser#genVidMD.
    def exitGenVidMD(self, ctx:commandsParser.GenVidMDContext):
        pass


    # Enter a parse tree produced by commandsParser#caption.
    def enterCaption(self, ctx:commandsParser.CaptionContext):
        pass

    # Exit a parse tree produced by commandsParser#caption.
    def exitCaption(self, ctx:commandsParser.CaptionContext):
        pass


    # Enter a parse tree produced by commandsParser#pathtoimg.
    def enterPathtoimg(self, ctx:commandsParser.PathtoimgContext):
        pass

    # Exit a parse tree produced by commandsParser#pathtoimg.
    def exitPathtoimg(self, ctx:commandsParser.PathtoimgContext):
        pass



del commandsParser
