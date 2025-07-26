#!/usr/bin/env python
"""
Loggerutil.

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : loggerutil
# @created     : Saturday Jul 26, 2025 08:25:51 IST
# @description :
# -*- coding: utf-8 -*-'
######################################################################
"""
import logging
import sys
import os
from typing import Optional, Union, Literal

LogLevel = Union[
    Literal[logging.CRITICAL],
    Literal[logging.ERROR],
    Literal[logging.WARNING],
    Literal[logging.INFO],
    Literal[logging.DEBUG],
    Literal[logging.NOTSET],
    int
]

class LoggerFactory:
    @staticmethod
    def get_logger(
        name: str,
        logfile: Optional[str] = None,
        level: LogLevel = logging.DEBUG,
        log_to_file: bool = False
    ) -> logging.Logger:
        """
        Creates and returns a logger that logs to stderr and optionally to a file.

        Args:
            name: Logger name (usually __name__).
            logfile: Path to the log file. Defaults to '<name>.log' if None.
            level: Logging level for the logger (default: DEBUG).
            log_to_file: If True, logs to a file in addition to stderr (default: False).

        Returns:
            A configured logger instance.
        """
        logger: logging.Logger = logging.getLogger(name)

        # Avoid adding handlers multiple times
        if logger.hasHandlers():
            return logger

        logger.setLevel(level)

        # Console handler (stderr)
        formatter: logging.Formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        stream_handler: logging.StreamHandler = logging.StreamHandler(sys.stderr)
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # File handler only if enabled
        if log_to_file:
            if logfile is None:
                # Default logfile name based on module name
                logfile = f"{name}.log"
                logfile = os.path.basename(logfile.replace('.', '_'))

            file_handler: logging.FileHandler = logging.FileHandler(logfile, mode='a')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger
