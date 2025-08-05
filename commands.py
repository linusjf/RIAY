#!/usr/bin/env python
"""Main command processor for ANTLR-generated command parser.

This module implements a listener for processing commands parsed by ANTLR.
It executes corresponding actions based on the parsed command syntax.
"""

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

from antlr4 import CommonTokenStream, FileStream, ParseTreeWalker

from commandsLexer import commandsLexer
from commandsParser import commandsParser
from commandsListener import commandsListener
from commandsverboselistener import CommandsVerboseListener
from commandsverbosestrategy import CommandsVerboseStrategy
from configconstants import ConfigConstants
from configenv import ConfigEnv
from loggerutil import LoggerFactory


# Initialize logger using LoggerFactory
config = ConfigEnv("config.env")
logger = LoggerFactory.get_logger(
    name=os.path.basename(__file__),
    level=logging.DEBUG,
    log_to_file=config.get(ConfigConstants.LOGGING, False)
)


class Commands(commandsListener):
    """Listener implementation for processing commands."""

    def __init__(self) -> None:
        """Initialize the command processor."""
        self.cwd = str(Path.cwd())
        self.exitcode = 0
        self.config = ConfigEnv("config.env")

    def enterAddvideo(self, ctx: commandsParser.AddvideoContext) -> None:
        """Process Addvideo command."""
        video_id = ctx.videoId().getText().strip('"')
        video_name = ctx.videoName().getText().strip('"')
        rule_name = self._get_rule_name(ctx)
        logger.info(f"Adding video '{video_id}' with name '{video_name}'.")
        self._execute_command([rule_name, video_id, video_name])

    def enterAddvideotoday(self, ctx: commandsParser.AddvideotodayContext) -> None:
        """Process Addvideotoday command."""
        video_id = ctx.videoId().getText().strip('"')
        day_of_year = int(ctx.dayofyear().getText())
        rule_name = self._get_rule_name(ctx)
        logger.info(f"Adding video '{video_id}' to day {day_of_year}.")
        self._execute_command([rule_name, video_id, str(day_of_year)])

    def enterAddimgtoday(self, ctx: commandsParser.AddimgtodayContext) -> None:
        """Process Addimgtoday command."""
        image_path = ctx.imagepath().getText().strip('"')
        caption = ctx.caption().getText().strip('"')
        day_of_year = int(ctx.dayofyear().getText())
        rule_name = self._get_rule_name(ctx)
        msg = f"Adding image '{image_path}' to day {day_of_year} with caption '{caption}'."
        logger.info(msg)
        self._execute_command([rule_name, image_path, caption, str(day_of_year)])

    def enterGenmonth(self, ctx: commandsParser.GenmonthContext) -> None:
        """Process Genmonth command."""
        rule_name = self._get_rule_name(ctx)
        month = ctx.month().getText()
        year = str(self.config.get(ConfigConstants.YEAR))
        if ctx.year() is not None:
            year = ctx.year().getText()
        logger.info(f"Generating month {month} for year {year}.")
        self._execute_command([rule_name, month, year])

    def enterLint(self, ctx: commandsParser.LintContext) -> None:
        """Process Lint command."""
        rule_name = self._get_rule_name(ctx)
        logger.info("Linting markdown docs...")
        self._execute_command([rule_name])

    def enterStitch(self, ctx: commandsParser.StitchContext) -> None:
        """Process Stitch command."""
        rule_name = self._get_rule_name(ctx)
        logger.info("Stitching...")
        self._execute_command([rule_name])

    def enterGentoc(self, ctx: commandsParser.GentocContext) -> None:
        """Process Gentoc command."""
        rule_name = self._get_rule_name(ctx)
        path_to_md = ctx.pathtomdfile().getText().strip('"')
        self._execute_command([rule_name, path_to_md])

    def enterEmbedarttoday(self, ctx:commandsParser.EmbedarttodayContext):
        """Process Embedarttoday command."""
        rule_name = self._get_rule_name(ctx)
        day_of_year = int(ctx.dayofyear().getText())
        logger.info(f"Embedding art to day {day_of_year}.")
        self._execute_command([rule_name, str(day_of_year)])

    def _get_rule_name(self, ctx) -> str:
        """Get the name of the current rule being processed.

        Args:
            ctx: The parser rule context

        Returns:
            The name of the rule as a string
        """
        rule_index = ctx.getRuleIndex()
        return ctx.parser.ruleNames[rule_index]

    def _execute_command(self, command: list[str]) -> None:
        """Execute a command line program.

        Args:
            command: A list containing the command line program and its options.
        """
        file_path = Path(self.cwd) / command[0]
        if file_path.exists():
            command[0] = str(file_path)

        try:
            result = subprocess.run(command, check=True)
            if result.returncode != 0:
                self.exitcode = 1
        except subprocess.CalledProcessError as e:
            logger.error("Command failed: %s", str(e))
            self.exitcode = 1
        except Exception as e:
            logger.error("Unexpected error executing command: %s", str(e))
            self.exitcode = 1


def main() -> None:
    """Main entry point for command processing."""
    parser = argparse.ArgumentParser(description='Process commands for the system.',
                                     epilog="""
     Parses the commands file named 'commands.txt' and executes each command sequentially
     """)

    # Parse known args first to handle help before processing commands file
    parser.parse_known_args()

    config = ConfigEnv("config.env")
    input_stream = FileStream(config.get(ConfigConstants.COMMANDS_FILE))
    lexer = commandsLexer(input_stream)
    lexer.removeErrorListeners()

    stream = CommonTokenStream(lexer)
    parser = commandsParser(stream)
    parser.setTrace(trace=False)
    parser.removeErrorListeners()
    parser.addErrorListener(CommandsVerboseListener())
    parser._errHandler = CommandsVerboseStrategy()  # pyright: ignore

    try:
        tree = parser.program()
        executor = Commands()
        walker = ParseTreeWalker()
        walker.walk(executor, tree)
        sys.exit(executor.exitcode)
    except Exception as e:
        logger.error("\nParsing failed: %s : %s", type(e).__name__, str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
