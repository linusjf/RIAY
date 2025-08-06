#!/usr/bin/env python
"""Custom verbose error strategy for command parsing."""

import os
import subprocess
from pathlib import Path
from antlr4.error.ErrorStrategy import DefaultErrorStrategy, InputMismatchException
from configenv import ConfigEnv
from configconstants import ConfigConstants
from loggerutil import LoggerFactory

class CommandsVerboseStrategy(DefaultErrorStrategy):
    """Custom verbose error strategy that bails on first error."""

    def __init__(self):
        super().__init__()
        self.config = ConfigEnv("config.env")
        self.logger = LoggerFactory.get_logger(
             name=os.path.basename(__file__),
             log_to_file=self.config.get(ConfigConstants.LOGGING, False))

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

        self.logger.error("\n🚨 Fatal Syntax Error (Bail):")
        self.logger.error(f"  ➤ At line {line}, column {column}")
        self.logger.error(f"  ➤ Offending token: {offending_text}")
        self.logger.error(f"  ➤ Rule stack: {stack}")
        self.logger.error(f"  ➤ Parser rules: {rule_names}")
        self.logger.error(f"  ➤ Expected tokens: {expected_tokens}")
        self.logger.error(f"  ➤ Error: {type(exception)} : {str(exception)}")

        # Show source line
        if hasattr(input_stream, "strdata"):
            try:
                full_line = input_stream.strdata.splitlines()[line - 1]
                self.logger.error(f"  ➤ Code: {full_line}")
                self.logger.error(" " * (column + 10) + "^")
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
            self.logger.info(f"Help for script {command}:\n")
            # Use subprocess.run to execute the command
            result = subprocess.run(cmd, shell=True, check=True)
            return result.returncode
        except subprocess.CalledProcessError as e:
            # If the command returns a non-zero exit code, raise an exception
            self.logger.error(e)
            self.exitcode = 1
        except Exception as e:
            # If any other exception occurs, raise it
            self.logger.error(f"Error executing help command: {str(e)}")
            raise
