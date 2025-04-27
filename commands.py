#!/usr/bin/env python
import logging
import subprocess
import sys
from pathlib import Path
from antlr4 import *
from commandsLexer import commandsLexer
from commandsParser import commandsParser
from commandsListener import commandsListener

class commands(commandsListener):

    def __init__(self):
        self.cwd = str(Path.cwd())
        self.exitcode = 0

    # Enter a parse tree produced by commandsParser#Addvideo.
    def enterAddvideo(self, ctx:commandsParser.AddvideoContext):
        videoId = ctx.videoId().getText().strip('"')
        videoName = ctx.videoName().getText().strip('"')
        ruleName = self.getRuleName(ctx)
        print(f"Adding video '{videoId}' with name '{videoName}'.")
        self.executeCommand([ruleName, videoId, videoName])

    # Enter a parse tree produced by commandsParser#Genmonth.
    def enterGenmonth(self, ctx:commandsParser.GenmonthContext):
        month = ctx.month().getText()
        year = ctx.year().getText()
        ruleName = self.getRuleName(ctx)
        print(f"Generating month {month} for year {year}.")
        self.executeCommand([ruleName, month, year])

    # Enter a parse tree produced by commandsParser#Lintall.
    def enterLintall(self, ctx:commandsParser.LintallContext):
        ruleName = self.getRuleName(ctx)
        print(f"Linting all...")
        self.executeCommand([ruleName])

    # Enter a parse tree produced by commandsParser#stitch.
    def enterStitch(self, ctx:commandsParser.StitchContext):
        ruleName = self.getRuleName(ctx)
        print(f"Stitching...")
        self.executeCommand([ruleName])

    # Enter a parse tree produced by commandsParser#gentoc.
    def enterGentoc(self, ctx:commandsParser.GentocContext):
        ruleName = self.getRuleName(ctx)
        pathtomdfile = ctx.pathtomdfile().getText().strip('"')
        self.executeCommand([ruleName, pathtomdfile])

    # Get Rule Name
    def getRuleName(self, ctx):
        ruleIndex = ctx.getRuleIndex()
        ruleName = ctx.parser.ruleNames[ruleIndex]
        return ruleName

    # Execute command
    def executeCommand(self, command:list[str]):
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
    input_stream = FileStream("commands.txt")
    lexer = commandsLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = commandsParser(stream)
    tree = parser.program()

    execute_commands = commands()
    walker = ParseTreeWalker()
    walker.walk(execute_commands, tree)
    sys.exit(execute_commands.exitcode)


if __name__ == "__main__":
    main()
