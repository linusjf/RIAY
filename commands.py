#!/usr/bin/env python
import logging
import subprocess
import sys
from pathlib import Path
from antlr4 import FileStream
from antlr4 import CommonTokenStream
from antlr4 import ParseTreeWalker
from commandsLexer import commandsLexer
from commandsParser import commandsParser
from commandsListener import commandsListener
from commandsverboselistener import commandsVerboseListener
from commandsverbosestrategy import commandsVerboseStrategy
from dotenv import load_dotenv
import os


class commands(commandsListener):

    def __init__(self):
        self.cwd = str(Path.cwd())
        self.exitcode = 0

    # Enter a parse tree produced by commandsParser#Addvideo.
    def enterAddvideo(self, ctx: commandsParser.AddvideoContext):
        videoId = ctx.videoId().getText().strip('"')
        videoName = ctx.videoName().getText().strip('"')
        ruleName = self.getRuleName(ctx)
        print(f"Adding video '{videoId}' with name '{videoName}'.")
        self.executeCommand([ruleName, videoId, videoName])

    # Enter a parse tree produced by commandsParser#addvideotoday.
    def enterAddvideotoday(self, ctx: commandsParser.AddvideotodayContext):
        videoId = ctx.videoId().getText().strip('"')
        dayofyear = int(ctx.dayofyear().getText())
        ruleName = self.getRuleName(ctx)
        print(f"Adding video '{videoId}' to day {dayofyear}.")
        self.executeCommand([ruleName, videoId, str(dayofyear)])

    # Enter a parse tree produced by commandsParser#addimgtoday.
    def enterAddimgtoday(self, ctx: commandsParser.AddimgtodayContext):
        imagepath = ctx.imagepath().getText().strip('"')
        caption = ctx.caption().getText().strip('""')
        dayofyear = int(ctx.dayofyear().getText())
        ruleName = self.getRuleName(ctx)
        print(
            f"Adding image '{imagepath}' to day {dayofyear} with caption '{caption}'."
        )
        self.executeCommand([ruleName, imagepath, caption, str(dayofyear)])

    # Enter a parse tree produced by commandsParser#Genmonth.
    def enterGenmonth(self, ctx: commandsParser.GenmonthContext):
        ruleName = self.getRuleName(ctx)
        month = ctx.month().getText()
        year = str(os.getenv("YEAR"))
        if ctx.year() is not None:
            year = ctx.year().getText()
        print(f"Generating month {month} for year {year}.")
        self.executeCommand([ruleName, month, year])

    # Enter a parse tree produced by commandsParser#Lintall.
    def enterLintall(self, ctx: commandsParser.LintallContext):
        ruleName = self.getRuleName(ctx)
        print(f"Linting all...")
        self.executeCommand([ruleName])

    # Enter a parse tree produced by commandsParser#stitch.
    def enterStitch(self, ctx: commandsParser.StitchContext):
        ruleName = self.getRuleName(ctx)
        print(f"Stitching...")
        self.executeCommand([ruleName])

    # Enter a parse tree produced by commandsParser#gentoc.
    def enterGentoc(self, ctx: commandsParser.GentocContext):
        ruleName = self.getRuleName(ctx)
        pathtomdfile = ctx.pathtomdfile().getText().strip('"')
        self.executeCommand([ruleName, pathtomdfile])

    # Get Rule Name
    def getRuleName(self, ctx):
        ruleIndex = ctx.getRuleIndex()
        ruleName = ctx.parser.ruleNames[ruleIndex]
        return ruleName

    # Execute command
    def executeCommand(self, command: list[str]):
        """
        Execute a command line program.
        Args:
            command (list[str]): A list of strings containing the command line program and its options.
        Returns:
            int: The return code of the executed command.
        """
        file_path = Path(self.cwd + "/" + command[0])
        if file_path.exists():
            command[0] = self.cwd + "/" + command[0]
        try:
            # Use subprocess.run to execute the command
            result = subprocess.run(command, check=True)
            return result.returncode
        except subprocess.CalledProcessError as e:
            # If the command returns a non-zero exit code, raise an exception
            logging.error(e)
            self.exitcode = 1
        except Exception as e:
            # If any other exception occurs, raise it
            raise Exception(f"Error executing command: {str(e)}")


def main():
    load_dotenv(dotenv_path="config.env")
    input_stream = FileStream("commands.txt")
    lexer = commandsLexer(input_stream)
    lexer.removeErrorListeners()
    stream = CommonTokenStream(lexer)
    parser = commandsParser(stream)
    parser.setTrace(trace=False)
    parser.removeErrorListeners()
    parser.addErrorListener(commandsVerboseListener())
    parser._errHandler = commandsVerboseStrategy()  # pyright: ignore
    try:
        tree = parser.program()
        execute_commands = commands()
        walker = ParseTreeWalker()
        walker.walk(execute_commands, tree)
        sys.exit(execute_commands.exitcode)
    except Exception as e:
        print(f"\nParsing failed: {type(e)} : {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
