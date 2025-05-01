#!/usr/bin/env python
"""
Commandsverbosestrategy.

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : commandsverbosestrategy
# @created     : Thursday May 01, 2025 08:59:42 IST
# @description :
# -*- coding: utf-8 -*-'
######################################################################
"""
import sys
import logging
from pathlib import Path
import subprocess
from antlr4.error.ErrorStrategy import DefaultErrorStrategy, InputMismatchException


class commandsVerboseStrategy(DefaultErrorStrategy):
    def recover(self, recognizer, e):
        self.report_error(recognizer, e.offendingToken, e)
        raise e  # Immediately throw

    def recoverInline(self, recognizer):
        token = recognizer.getCurrentToken()
        e = InputMismatchException(recognizer)
        self.report_error(recognizer, token, e)
        raise e  # Immediately throw

    def sync(self, recognizer):
        # Don't try error recovery via token resync
        pass

    def report_error(self, recognizer, offendingToken, exception):
        rule_names = recognizer.ruleNames
        stack = recognizer.getRuleInvocationStack()
        stack = list(reversed(stack))
        expected_tokens = recognizer.getExpectedTokens().toString(
            recognizer.literalNames, recognizer.symbolicNames
        )

        line = offendingToken.line
        column = offendingToken.column
        offending_text = offendingToken.text
        input_stream = offendingToken.getInputStream()

        print("\n🚨 Fatal Syntax Error (Bail):")
        print(f"  ➤ At line {line}, column {column}")
        print(f"  ➤ Offending token: {offending_text}")
        print(f"  ➤ Rule stack: {stack}")
        print(f"  ➤ Parser rules: {rule_names}")
        print(f"  ➤ Expected tokens: {expected_tokens}")
        print(f"  ➤ Error: {type(exception)} : {str(exception)}")

        # show source line
        if hasattr(input_stream, "strdata"):
            try:
                full_line = input_stream.strdata.splitlines()[line - 1]
                print(f"  ➤ Code: {full_line}")
                print(" " * (column + 10) + "^")
                commandName = full_line.split()[0]
                self.executeHelpCommand(commandName)
            except IndexError:
                pass

    # Execute help command
    def executeHelpCommand(self, command: str):
        """
        Execute a command line program.
        Args:
            command (str): A string containing the command line program.
        Returns:
            int: The return code of the executed command.
        """
        cwd = str(Path.cwd())
        cmd = ""
        file_path = Path(cwd + "/" + command)
        if file_path.exists():
            cmd = cwd + "/" + command + " --help"
        try:
            print(f"Help for script {command}:\n", file=sys.stderr)
            # Use subprocess.run to execute the command
            result = subprocess.run(cmd, shell=True, check=True)
            return result.returncode
        except subprocess.CalledProcessError as e:
            # If the command returns a non-zero exit code, raise an exception
            logging.error(e)
            self.exitcode = 1
        except Exception as e:
            # If any other exception occurs, raise it
            raise Exception(f"Error executing help command: {str(e)}")
