#!/usr/bin/env python
import subprocess
import sys
from pathlib import Path
from antlr4 import *
from commandsLexer import commandsLexer
from commandsParser import commandsParser
from commandsListener import commandsListener

class commands(commandsListener):

    def __init__(self):
        self.cwd = Path.cwd()

    # Enter a parse tree produced by commandsParser#addVideo.
    def enterAddVideo(self, ctx:commandsParser.AddVideoContext):
        videoId = ctx.videoId().getText().strip('"')
        videoName = ctx.videoName().getText().strip('"')
        print(f"Adding video '{videoId}' with name '{videoName}'")

    # Enter a parse tree produced by commandsParser#genMonth.
    def enterGenMonth(self, ctx:commandsParser.GenMonthContext):
        month = ctx.month().getText()
        year = ctx.year().getText()
        print(f"Generating month {month} for year {year}")

    # Enter a parse tree produced by commandsParser#lintAll.
    def enterLintAll(self, ctx:commandsParser.LintAllContext):
        print("Linting all")

    # Enter a parse tree produced by commandsParser#genVidMD.
    def enterGenVidMD(self, ctx:commandsParser.GenVidMDContext):
        videoId = ctx.videoId().getText().strip('"')
        caption = ctx.caption().getText().strip('"')
        pathtoimg = ctx.pathtoimg().getText().strip('"')
        print(f"Generating video markdown for '{videoId}' with caption '{caption}' and image '{pathtoimg}'")


def main():
    input_stream = FileStream("commands.txt")
    lexer = commandsLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = commandsParser(stream)
    tree = parser.program()

    execute_commands = commands()
    print(execute_commands.cwd)
    walker = ParseTreeWalker()
    walker.walk(execute_commands, tree)


if __name__ == "__main__":
    main()
