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


    # Enter a parse tree produced by commandsParser#command.
    def enterCommand(self, ctx:commandsParser.CommandContext):
        pass

    # Exit a parse tree produced by commandsParser#command.
    def exitCommand(self, ctx:commandsParser.CommandContext):
        pass


    # Enter a parse tree produced by commandsParser#addvideo.
    def enterAddvideo(self, ctx:commandsParser.AddvideoContext):
        pass

    # Exit a parse tree produced by commandsParser#addvideo.
    def exitAddvideo(self, ctx:commandsParser.AddvideoContext):
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


    # Enter a parse tree produced by commandsParser#genmonth.
    def enterGenmonth(self, ctx:commandsParser.GenmonthContext):
        pass

    # Exit a parse tree produced by commandsParser#genmonth.
    def exitGenmonth(self, ctx:commandsParser.GenmonthContext):
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


    # Enter a parse tree produced by commandsParser#lint.
    def enterLint(self, ctx:commandsParser.LintContext):
        pass

    # Exit a parse tree produced by commandsParser#lint.
    def exitLint(self, ctx:commandsParser.LintContext):
        pass


    # Enter a parse tree produced by commandsParser#stitch.
    def enterStitch(self, ctx:commandsParser.StitchContext):
        pass

    # Exit a parse tree produced by commandsParser#stitch.
    def exitStitch(self, ctx:commandsParser.StitchContext):
        pass


    # Enter a parse tree produced by commandsParser#gentoc.
    def enterGentoc(self, ctx:commandsParser.GentocContext):
        pass

    # Exit a parse tree produced by commandsParser#gentoc.
    def exitGentoc(self, ctx:commandsParser.GentocContext):
        pass


    # Enter a parse tree produced by commandsParser#pathtomdfile.
    def enterPathtomdfile(self, ctx:commandsParser.PathtomdfileContext):
        pass

    # Exit a parse tree produced by commandsParser#pathtomdfile.
    def exitPathtomdfile(self, ctx:commandsParser.PathtomdfileContext):
        pass


    # Enter a parse tree produced by commandsParser#addvideotoday.
    def enterAddvideotoday(self, ctx:commandsParser.AddvideotodayContext):
        pass

    # Exit a parse tree produced by commandsParser#addvideotoday.
    def exitAddvideotoday(self, ctx:commandsParser.AddvideotodayContext):
        pass


    # Enter a parse tree produced by commandsParser#dayofyear.
    def enterDayofyear(self, ctx:commandsParser.DayofyearContext):
        pass

    # Exit a parse tree produced by commandsParser#dayofyear.
    def exitDayofyear(self, ctx:commandsParser.DayofyearContext):
        pass


    # Enter a parse tree produced by commandsParser#addimgtoday.
    def enterAddimgtoday(self, ctx:commandsParser.AddimgtodayContext):
        pass

    # Exit a parse tree produced by commandsParser#addimgtoday.
    def exitAddimgtoday(self, ctx:commandsParser.AddimgtodayContext):
        pass


    # Enter a parse tree produced by commandsParser#imagepath.
    def enterImagepath(self, ctx:commandsParser.ImagepathContext):
        pass

    # Exit a parse tree produced by commandsParser#imagepath.
    def exitImagepath(self, ctx:commandsParser.ImagepathContext):
        pass


    # Enter a parse tree produced by commandsParser#caption.
    def enterCaption(self, ctx:commandsParser.CaptionContext):
        pass

    # Exit a parse tree produced by commandsParser#caption.
    def exitCaption(self, ctx:commandsParser.CaptionContext):
        pass


    # Enter a parse tree produced by commandsParser#embedarttoday.
    def enterEmbedarttoday(self, ctx:commandsParser.EmbedarttodayContext):
        pass

    # Exit a parse tree produced by commandsParser#embedarttoday.
    def exitEmbedarttoday(self, ctx:commandsParser.EmbedarttodayContext):
        pass



del commandsParser