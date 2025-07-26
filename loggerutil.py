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
from typing import Optional

class LoggerFactory:
    @staticmethod
    def get_logger(
        name: str,
        level: int = logging.INFO,
        logfile: Optional[str] = None,
        log_to_file: bool = False
    ) -> logging.Logger:
        """
        Creates and returns a logger that logs to stderr and optionally to a file.

        Args:
            name: Logger name (usually __name__).
            level: Logging level for the logger (default: INFO).
            logfile: Path to the log file. Defaults to '<name>.log' if None.
            log_to_file: If True, logs to a file in addition to stderr (default: False).

        Returns:
            A configured logger instance.
        """
        if name == "__main__":
            name = os.path.splitext(os.path.basename(sys.argv[0]))[0]

        logger: logging.Logger = logging.getLogger(name)
        logger.propagate = False

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
