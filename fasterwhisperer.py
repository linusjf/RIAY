#!/usr/bin/env python3
"""Transcribe audio files using faster-whisper library.

This module provides functionality to transcribe audio files using the
faster-whisper implementation of OpenAI's Whisper model.
"""

import argparse
import os
import time

import torch
from faster_whisper import WhisperModel

from configenv import ConfigEnv
from configconstants import ConfigConstants
from loggerutil import LoggerFactory

# Load environment variables from config.env
config = ConfigEnv('config.env')
MODEL_SIZE = config.get(ConfigConstants.ASR_LOCAL_MODEL)
BEAM_SIZE = config.get(ConfigConstants.ASR_BEAM_SIZE)
ASR_INITIAL_PROMPT = config.get(ConfigConstants.ASR_INITIAL_PROMPT)
ASR_CARRY_INITIAL_PROMPT = config.get(ConfigConstants.ASR_CARRY_INITIAL_PROMPT)

# Initialize logger
logger = LoggerFactory.get_logger(
    name=os.path.basename(__file__),
    log_to_file=config.get(ConfigConstants.LOGGING, False)
)

def transcribe_audio(
    audio_file: str,
    model_size: str = MODEL_SIZE,
    beam_size: int = BEAM_SIZE,
    device: str = "cpu",
    compute_type: str = "int8",
) -> None:
    """Transcribe audio file using faster-whisper model.

    Args:
        audio_file: Path to audio file to transcribe.
        model_size: Size of whisper model to use.
        beam_size: Beam size for decoding.
        device: Device to run model on ('cuda' or 'cpu').
        compute_type: Compute type for model ('float16', 'int8_float16', etc.).
    """
    start_time = time.time()
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    logger.info(
        f"Executing faster-whisper with device '{device}' and compute type '{compute_type}' "
        f"with device name {torch.cuda.get_device_name(0) if device == 'cuda' else 'CPU'}"
    )

    segments, info = model.transcribe(
        audio_file,
        beam_size=beam_size,
        initial_prompt=ASR_INITIAL_PROMPT,
        condition_on_previous_text=ASR_CARRY_INITIAL_PROMPT
    )

    logger.info(
        f"Detected language '{info.language}' with probability {info.language_probability}"
    )

    for segment in segments:
        print(segment.text, end='', flush=True)
    print()

    end_time = time.time()
    logger.info(f"Transcribed audio in {end_time - start_time:.2f} seconds")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description='Transcribe audio files using faster-whisper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  %(prog)s audio.mp3
  %(prog)s audio.wav --model-size large
"""
    )
    parser.add_argument(
        'audio_file',
        help='Path to audio file to transcribe'
    )
    parser.add_argument(
        '--model-size',
        default=MODEL_SIZE,
        help=f'Size of whisper model to use (default: {MODEL_SIZE})'
    )
    return parser.parse_args()


def main() -> None:
    """Run main transcription function."""
    args = parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"
    transcribe_audio(
        args.audio_file,
        model_size=args.model_size,
        device=device,
        compute_type=compute_type
    )


if __name__ == "__main__":
    main()
