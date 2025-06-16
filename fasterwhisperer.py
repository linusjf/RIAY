#!/usr/bin/env python3
"""Transcribe audio files using faster-whisper library.

This module provides functionality to transcribe audio files using the
faster-whisper implementation of OpenAI's Whisper model.
"""

import sys
import argparse
import os
from dotenv import load_dotenv
import torch
from faster_whisper import WhisperModel


# Load environment variables from config.env
load_dotenv('config.env')
MODEL_SIZE = os.getenv('ASR_LOCAL_MODEL', 'base')
BEAM_SIZE = int(os.getenv('ASR_BEAM_SIZE', 3))
ASR_INITIAL_PROMPT= os.getenv('ASR_INITIAL_PROMPT', '')

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
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    print(
        "Executing faster-whisper with device '%s' and compute type '%s' with device name %s"
        % (device, compute_type, torch.cuda.get_device_name(0)), file=sys.stderr, flush=True)

    segments, info = model.transcribe(audio_file, beam_size=beam_size, initial_prompt=ASR_INITIAL_PROMPT)

    print(
        "Detected language '%s' with probability %f"
        % (info.language, info.language_probability), file=sys.stderr, flush=True)

    for segment in segments:
        print(segment.text, end='', flush=True)
    print("")

def main() -> None:
    """Run main transcription function."""
    parser = argparse.ArgumentParser(description='Transcribe audio files using faster-whisper')
    parser.add_argument('audio_file', help='Path to audio file to transcribe')
    parser.add_argument('--model-size', default=MODEL_SIZE,
                       help=f'Size of whisper model to use (default: {MODEL_SIZE})')
    args = parser.parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"
    transcribe_audio(args.audio_file, model_size=args.model_size, device=device, compute_type=compute_type)


if __name__ == "__main__":
    main()
