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
        self.cwd = str(Path.cwd())

    # Enter a parse tree produced by commandsParser#addVideo.
    def enterAddvideo(self, ctx:commandsParser.AddvideoContext):
        videoId = ctx.videoId().getText().strip('"')
        videoName = ctx.videoName().getText().strip('"')
        ruleIndex = ctx.getRuleIndex()
        ruleName = ctx.parser.ruleNames[ruleIndex]
        print(f"Rule {ruleName}: Adding video '{videoId}' with name '{videoName}'")
        self.executeCommand([ruleName, videoId, videoName])

    # Enter a parse tree produced by commandsParser#genMonth.
    def enterGenmonth(self, ctx:commandsParser.GenmonthContext):
        month = ctx.month().getText()
        year = ctx.year().getText()
        ruleIndex = ctx.getRuleIndex()
        ruleName = ctx.parser.ruleNames[ruleIndex]
        print(f"Rule {ruleName}: Generating month {month} for year {year}")
        self.executeCommand([ruleName, month, year])

    # Enter a parse tree produced by commandsParser#lintAll.
    def enterLintall(self, ctx:commandsParser.LintallContext):
        ruleIndex = ctx.getRuleIndex()
        ruleName = ctx.parser.ruleNames[ruleIndex]
        print(f"Rule {ruleName}: Linting all")
        self.executeCommand([ruleName])

    # Enter a parse tree produced by commandsParser#genVidMD.
    def enterGenvidmd(self, ctx:commandsParser.GenvidmdContext):
        videoId = ctx.videoId().getText().strip('"')
        caption = ctx.caption().getText().strip('"')
        pathtoimg = ctx.pathtoimg().getText().strip('"')
        ruleIndex = ctx.getRuleIndex()
        ruleName = ctx.parser.ruleNames[ruleIndex]
        print(f"Rule {ruleName}: Generating video markdown for '{videoId}' with caption '{caption}' and image '{pathtoimg}'")
        self.executeCommand([ruleName, videoId, caption, pathtoimg])

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
            raise Exception(f"Command failed with return code {e.returncode}")
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
    print(execute_commands.cwd)
    walker = ParseTreeWalker()
    walker.walk(execute_commands, tree)


if __name__ == "__main__":
    main()
