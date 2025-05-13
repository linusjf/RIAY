from antlr4.error.ErrorListener import ErrorListener
from antlr4 import Token


class CommandsVerboseListener(ErrorListener):
    """Custom verbose error listener for command parsing."""

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        """Handle syntax errors with detailed reporting."""
        rule_names = recognizer.ruleNames
        stack = recognizer.getRuleInvocationStack()
        stack = list(reversed(stack))
        expected_tokens = recognizer.getExpectedTokens().toString(
            recognizer.literalNames, recognizer.symbolicNames
        )

        print("\n🛑 Syntax Error:")
        print(f"  ➤ At line {line}, column {column}")
        print(
            f"  ➤ Offending token: {offendingSymbol.text if isinstance(offendingSymbol, Token) else offendingSymbol}"
        )
        print(f"  ➤ Message: {msg}")
        print(f"  ➤ Rule stack: {stack}")
        print(f"  ➤ Parser rules: {rule_names}")
        print(f"  ➤ Expected: {expected_tokens}")
        print(f"  ➤ Error: {type(e)} : {e}")

        # Print the full line with a pointer
        input_stream = offendingSymbol.getInputStream()
        full_line = input_stream.strdata.splitlines()[line - 1]
        print(f"  ➤ Code: {full_line}")
        print(" " * (column + 10) + "^")
