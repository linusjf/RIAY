#!/usr/bin/env python
"""Custom verbose error strategy for command parsing."""

import sys
import logging
from pathlib import Path
import subprocess
from antlr4.error.ErrorStrategy import DefaultErrorStrategy, InputMismatchException


class CommandsVerboseStrategy(DefaultErrorStrategy):
    """Custom verbose error strategy that bails on first error."""

    def recover(self, recognizer, e):
        """Report error and raise immediately."""
        self.report_error(recognizer, e.offendingToken, e)
        raise e  # Immediately throw

    def recoverInline(self, recognizer):
        """Report inline error and raise immediately."""
        token = recognizer.getCurrentToken()
        e = InputMismatchException(recognizer)
        self.report_error(recognizer, token, e)
        raise e  # Immediately throw

    def sync(self, recognizer):
        """Don't try error recovery via token resync."""
        pass

    def report_error(self, recognizer, offending_token, exception):
        """Generate detailed error report."""
        rule_names = recognizer.ruleNames
        stack = recognizer.getRuleInvocationStack()
        stack = list(reversed(stack))
        expected_tokens = recognizer.getExpectedTokens().toString(
            recognizer.literalNames, recognizer.symbolicNames
        )

        line = offending_token.line
        column = offending_token.column
        offending_text = offending_token.text
        input_stream = offending_token.getInputStream()

        print("\n🚨 Fatal Syntax Error (Bail):")
        print(f"  ➤ At line {line}, column {column}")
        print(f"  ➤ Offending token: {offending_text}")
        print(f"  ➤ Rule stack: {stack}")
        print(f"  ➤ Parser rules: {rule_names}")
        print(f"  ➤ Expected tokens: {expected_tokens}")
        print(f"  ➤ Error: {type(exception)} : {str(exception)}")

        # Show source line
        if hasattr(input_stream, "strdata"):
            try:
                full_line = input_stream.strdata.splitlines()[line - 1]
                print(f"  ➤ Code: {full_line}")
                print(" " * (column + 10) + "^")
                command_name = full_line.split()[0]
                self.execute_help_command(command_name)
            except IndexError:
                pass

    def execute_help_command(self, command):
        """
        Execute a command line program to show help.
        
        Args:
            command: A string containing the command line program.
        
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
