#!/usr/bin/env python3
"""Transcribe audio files using faster-whisper library.

This module provides functionality to transcribe audio files using the
faster-whisper implementation of OpenAI's Whisper model.
"""

import argparse
from faster_whisper import WhisperModel


MODEL_SIZE = "tiny"
BEAM_SIZE = 5


def transcribe_audio(
    audio_file: str,
    model_size: str = MODEL_SIZE,
    beam_size: int = BEAM_SIZE,
    device: str = "cuda",
    compute_type: str = "float16",
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
    segments, info = model.transcribe(audio_file, beam_size=beam_size)

    print(
        "Detected language '%s' with probability %f"
        % (info.language, info.language_probability)
    )

    for segment in segments:
        print(segment.text)


def main() -> None:
    """Run main transcription function."""
    parser = argparse.ArgumentParser(description='Transcribe audio files using faster-whisper')
    parser.add_argument('audio_file', help='Path to audio file to transcribe')
    parser.add_argument('--model-size', default=MODEL_SIZE,
                       help=f'Size of whisper model to use (default: {MODEL_SIZE})')
    args = parser.parse_args()

    transcribe_audio(args.audio_file, model_size=args.model_size)


if __name__ == "__main__":
    main()
