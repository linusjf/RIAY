from antlr4.error.ErrorListener import ErrorListener
from antlr4 import Token
import os
from configenv import ConfigEnv
from configconstants import ConfigConstants
from loggerutil import LoggerFactory


class CommandsVerboseListener(ErrorListener):
    """Custom verbose error listener for command parsing."""

    def __init__(self):
        super().__init__()
        self.config = ConfigEnv("config.env")
        self.logger = LoggerFactory.get_logger(
            name=os.path.basename(__file__),
            log_to_file=self.config.get(ConfigConstants.LOGGING, False)
        )

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        """Handle syntax errors with detailed reporting."""
        rule_names = recognizer.ruleNames
        stack = recognizer.getRuleInvocationStack()
        stack = list(reversed(stack))
        expected_tokens = recognizer.getExpectedTokens().toString(
            recognizer.literalNames, recognizer.symbolicNames
        )

        self.logger.error("\n🛑 Syntax Error:")
        self.logger.error(f"  ➤ At line {line}, column {column}")
        self.logger.error(
            f"  ➤ Offending token: {offendingSymbol.text if isinstance(offendingSymbol, Token) else offendingSymbol}"
        )
        self.logger.error(f"  ➤ Message: {msg}")
        self.logger.error(f"  ➤ Rule stack: {stack}")
        self.logger.error(f"  ➤ Parser rules: {rule_names}")
        self.logger.error(f"  ➤ Expected: {expected_tokens}")
        self.logger.error(f"  ➤ Error: {type(e)} : {e}")

        # Print the full line with a pointer
        input_stream = offendingSymbol.getInputStream()
        full_line = input_stream.strdata.splitlines()[line - 1]
        self.logger.error(f"  ➤ Code: {full_line}")
        self.logger.error(" " * (column + 10) + "^")
