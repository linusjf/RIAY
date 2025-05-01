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
            except IndexError:
                pass
