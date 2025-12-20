#!/usr/bin/env python3
"""
Transcribe YouTube videos using OpenAI Whisper API.
Downloads audio from YouTube and sends to Whisper for transcription.
"""

import argparse
import sys
import subprocess
import time
import logging
from pathlib import Path
import urllib.request
import urllib.error
from typing import List, Optional
import os

# Add the script directory to the path to import local modules
SCRIPT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(SCRIPT_DIR))

# Import ConfigEnv and ConfigConstants
try:
    from configenv import ConfigEnv
    from configconstants import ConfigConstants
    from loggerutil import LoggerFactory
except ImportError:
    # Add parent directory to path for direct imports
    sys.path.insert(0, str(SCRIPT_DIR.parent))
    from configenv import ConfigEnv
    from configconstants import ConfigConstants
    from loggerutil import LoggerFactory

VERSION = "1.0.0"
SCRIPT_NAME = Path(__file__).name
FASTER_WHISPER = "faster-whisper"
MAX_CHUNK_DURATION = 600  # 10 minutes in seconds


class VideoTranscriber:
    """Class for transcribing YouTube videos using OpenAI Whisper API."""

    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize with configuration."""
        config = ConfigEnv(config_path if config_path else str(SCRIPT_DIR / "config.env"), 
                          override=True, include_os_env=True)
        
        self.logger = LoggerFactory.get_logger(
            name=os.path.basename(__file__),
            log_to_file=config.get(ConfigConstants.LOGGING, False)
        )
        
        self.config = config
        self.script_dir = SCRIPT_DIR
        
        # Load configuration values
        self.required_vars = [
            ConfigConstants.OPENAI_API_KEY,
            ConfigConstants.CAPTIONS_OUTPUT_DIR,
            ConfigConstants.ASR_LLM_API_KEY,
            ConfigConstants.ASR_LLM_BASE_URL,
            ConfigConstants.ASR_LLM_ENDPOINT,
            ConfigConstants.ASR_LLM_MODEL,
            ConfigConstants.ASR_LOCAL_MODEL,
            ConfigConstants.TRANSCRIBE_LOCALLY,
            ConfigConstants.ENABLE_FAILOVER_MODE,
            ConfigConstants.ASR_INITIAL_PROMPT,
            ConfigConstants.ASR_BEAM_SIZE
        ]
        
        self.logger.debug(f"Initialized VideoTranscriber with config_path={config_path}")

    @staticmethod
    def is_package_installed(package_name: str) -> bool:
        """Check if a Python package is installed."""
        try:
            __import__(package_name)
            return True
        except ImportError:
            return False

    def check_video_exists(self, video_id: str) -> bool:
        """Check if a YouTube video exists and is accessible."""
        try:
            # Try to access the video via YouTube's oembed endpoint
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"

            # Set a reasonable timeout
            request = urllib.request.Request(oembed_url)
            request.add_header('User-Agent', 'Mozilla/5.0 (compatible; YouTubeVideoChecker/1.0)')

            try:
                response = urllib.request.urlopen(request, timeout=10)
                # If we get a successful response (status 200), the video exists
                if response.status == 200:
                    self.logger.debug(f"Video {video_id} exists and is accessible")
                    return True
            except urllib.error.HTTPError as e:
                # 404 means video doesn't exist or is private
                if e.code == 404:
                    self.logger.debug(f"Video {video_id} not found (404)")
                    return False
                # Other HTTP errors might indicate temporary issues
                self.logger.warning(f"HTTP error checking video {video_id}: {e.code}")
                # For other errors, we'll still try to download (might be temporary)
                return True
            except urllib.error.URLError as e:
                self.logger.warning(f"URL error checking video {video_id}: {e.reason}")
                # Network issues - we'll still try to download
                return True

            return False
        except Exception as e:
            self.logger.warning(f"Error checking if video {video_id} exists: {e}")
            # If the check fails for any reason, we'll still try to download
            # and let the download process fail if the video truly doesn't exist
            return True

    def check_local_prerequisites(self) -> bool:
        """Check if local transcription prerequisites are available."""
        try:
            # Check for ffmpeg
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            # Check for whisper command
            subprocess.run(["whisper", "--help"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_audio_duration(self, audio_file: str) -> float:
        """Get the duration of an audio file in seconds using ffprobe."""
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                audio_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            duration = float(result.stdout.strip())
            self.logger.info(f"Audio file duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
            return duration
        except (subprocess.CalledProcessError, FileNotFoundError, ValueError) as e:
            self.logger.error(f"Failed to get audio duration: {e}")
            raise RuntimeError(f"Could not determine audio file duration: {e}")

    def split_audio_file(self, audio_file: str, chunk_duration: int = MAX_CHUNK_DURATION) -> List[str]:
        """
        Split audio file into chunks of specified duration.
        Returns list of chunk file paths.
        """
        try:
            # Get total duration
            total_duration = self.get_audio_duration(audio_file)

            # Calculate number of chunks needed
            num_chunks = int(total_duration // chunk_duration) + (1 if total_duration % chunk_duration > 0 else 0)

            if num_chunks <= 1:
                self.logger.info(f"Audio file is {total_duration/60:.2f} minutes, no splitting needed")
                return [audio_file]

            self.logger.info(f"Splitting {total_duration/60:.2f} minute audio into {num_chunks} chunks")

            audio_path = Path(audio_file)
            chunk_files = []

            for i in range(num_chunks):
                start_time = i * chunk_duration
                chunk_filename = f"{audio_path.stem}_chunk_{i:03d}{audio_path.suffix}"
                chunk_file = audio_path.parent / chunk_filename

                cmd = [
                    "ffmpeg",
                    "-i", audio_file,
                    "-ss", str(start_time),
                    "-t", str(chunk_duration),
                    "-c", "copy",
                    "-y",  # Overwrite output file if exists
                    str(chunk_file)
                ]

                self.logger.debug(f"Creating chunk {i+1}/{num_chunks}: {chunk_filename}")
                subprocess.run(cmd, capture_output=True, check=True)
                chunk_files.append(str(chunk_file))

            self.logger.info(f"Created {len(chunk_files)} chunk files")
            return chunk_files

        except Exception as e:
            self.logger.error(f"Failed to split audio file: {e}")
            raise

    def transcribe_via_openai_api(self, audio_file: str) -> str:
        """Transcribe audio using OpenAI Whisper API directly."""
        try:
            # Import OpenAI client
            from openai import OpenAI

            # Get base URL and endpoint from config
            base_url = self.config.get(ConfigConstants.ASR_LLM_BASE_URL)

            if not base_url:
                self.logger.error("ASR_LLM_BASE_URL not configured")
                raise ValueError("ASR_LLM_BASE_URL not configured")

            full_url = base_url

            self.logger.info(f"Transcribing with OpenAI Whisper API using endpoint: {full_url}")

            # Initialize OpenAI client with API key and custom base URL
            client = OpenAI(
                api_key=self.config.get(ConfigConstants.ASR_LLM_API_KEY),
                base_url=full_url
            )

            # Open the audio file
            with open(audio_file, 'rb') as audio:
                # Call the OpenAI Whisper API
                response = client.audio.transcriptions.create(
                    model=self.config.get(ConfigConstants.ASR_LLM_MODEL),
                    file=audio,
                    response_format="text",
                    prompt=self.config.get(ConfigConstants.ASR_INITIAL_PROMPT, ''),
                    language="en"
                )

            # The response is already text when response_format="text"
            return response

        except ImportError:
            self.logger.error("OpenAI Python library not installed. Install with: pip install openai")
            raise
        except Exception as e:
            self.logger.error(f"OpenAI API transcription failed: {e}")
            raise

    def transcribe_locally(self, audio_file: str) -> str:
        """Transcribe audio using local installation."""
        if self.config.get(ConfigConstants.USE_FASTER_WHISPER, False):
            try:
                if self.is_package_installed(FASTER_WHISPER):
                    # Run fasterwhisperer.py script
                    result = subprocess.run(
                        [sys.executable, str(self.script_dir / "fasterwhisperer.py"), audio_file],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    return result.stdout
                else:
                    self.logger.error(f"Python package {FASTER_WHISPER} not available")
                    raise RuntimeError(f"Package {FASTER_WHISPER} not installed")
            except Exception as e:
                self.logger.error(f"Faster whisper transcription failed: {e}")
                raise
        else:
            if self.check_local_prerequisites():
                try:
                    cmd = [
                        "whisper",
                        "--task", "transcribe",
                        "--model", self.config.get(ConfigConstants.ASR_LOCAL_MODEL, 'base'),
                        "--output_format", "txt",
                        "--language", "en",
                        "--initial_prompt", self.config.get(ConfigConstants.ASR_INITIAL_PROMPT, ''),
                        "--carry_initial_propmt", str(self.config.get(ConfigConstants.ASR_CARRY_INITIAL_PROMPT, 'false')).lower(),
                        "--beam_size", str(self.config.get(ConfigConstants.ASR_BEAM_SIZE, 5)),
                        audio_file
                    ]

                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        check=True
                    )

                    # Whisper saves output to a file with same base name
                    output_file = Path(audio_file).with_suffix('.txt')
                    if output_file.exists():
                        return output_file.read_text()
                    else:
                        raise FileNotFoundError(f"Output file not found: {output_file}")
                except Exception as e:
                    self.logger.error(f"Local whisper transcription failed: {e}")
                    raise
            else:
                self.logger.error("ffmpeg and/or whisper not available")
                raise RuntimeError("Local transcription prerequisites not met")

    def transcribe_audio_chunks(self, audio_file: str) -> str:
        """Transcribe audio file, splitting into chunks if longer than MAX_CHUNK_DURATION."""
        self.logger.info("Transcribing with Whisper...")
        start_time = time.time()

        try:
            # Check if we should use local transcription
            use_local = self.config.get(ConfigConstants.TRANSCRIBE_LOCALLY, False)

            # Get audio duration and split if needed
            try:
                duration = self.get_audio_duration(audio_file)
                if duration > MAX_CHUNK_DURATION:
                    self.logger.info(f"Audio file is {duration/60:.2f} minutes, splitting into chunks")
                    chunk_files = self.split_audio_file(audio_file)

                    # Transcribe each chunk
                    all_transcripts = []
                    for i, chunk_file in enumerate(chunk_files):
                        self.logger.info(f"Transcribing chunk {i+1}/{len(chunk_files)}")

                        if use_local:
                            chunk_transcript = self.transcribe_locally(chunk_file)
                        else:
                            chunk_transcript = self.transcribe_via_openai_api(chunk_file)

                        all_transcripts.append(chunk_transcript)

                        # Clean up chunk file
                        try:
                            Path(chunk_file).unlink()
                            self.logger.debug(f"Deleted chunk file: {chunk_file}")
                        except OSError as e:
                            self.logger.warning(f"Could not delete chunk file {chunk_file}: {e}")

                    # Combine all transcripts
                    combined_transcript = "\n\n".join(all_transcripts)
                    self.logger.info(f"Combined {len(chunk_files)} chunks into final transcript")

                    duration = time.time() - start_time
                    self.logger.info(f"Transcribed video in {duration:.2f} seconds")
                    return combined_transcript
                else:
                    # File is short enough, transcribe normally
                    self.logger.info(f"Audio file is {duration/60:.2f} minutes, transcribing as single file")
                    if use_local:
                        return self.transcribe_locally(audio_file)
                    else:
                        return self.transcribe_via_openai_api(audio_file)

            except Exception as e:
                self.logger.error(f"Failed to process audio file: {e}")
                raise

        except Exception as e:
            # Handle failover mode for API transcription
            if not use_local and self.config.get(ConfigConstants.ENABLE_FAILOVER_MODE, True):
                self.logger.warning(f"Chunked transcription failed: {e}. Trying single file transcription...")
                try:
                    if use_local:
                        return self.transcribe_locally(audio_file)
                    else:
                        return self.transcribe_via_openai_api(audio_file)
                except Exception as e2:
                    self.logger.error(f"Fallback transcription also failed: {e2}")
                    raise
            else:
                raise

    def transcribe_audio(self, audio_file: str) -> str:
        """Transcribe audio file using appropriate method (wrapper for backward compatibility)."""
        return self.transcribe_audio_chunks(audio_file)

    def dry_run(self, video_id: str, output_file: str) -> None:
        """Perform dry run without actual processing."""
        self.logger.info(f"DRY RUN: Would process video ID: {video_id}")
        self.logger.info(f"DRY RUN: Would create output file: {output_file}")
        self.logger.info("DRY RUN: Would download audio using downloadaudio script")
        self.logger.info("DRY RUN: Would check audio duration and split if > 10 minutes")
        self.logger.info("DRY RUN: Would transcribe and/or translate audio using Whisper API")
        self.logger.info("DRY RUN: Would clean up temporary files")

    def check_required_config(self) -> bool:
        """Check if all required configuration variables are present."""
        for var in self.required_vars:
            if self.config.get(var) is None:
                self.logger.error(f"Required configuration variable not found: {var}")
                return False
        return True

    def transcribe_video(self, video_id: str, output_file: Optional[str] = None, 
                        verbose: bool = False, debug: bool = False, 
                        dry_run: bool = False) -> bool:
        """Main method to transcribe a video."""
        
        # Set logging level based on arguments
        if debug:
            self.logger.setLevel(logging.DEBUG)
        elif verbose:
            self.logger.setLevel(logging.INFO)
        
        # Check required configuration
        if not self.check_required_config():
            return False

        # Determine output file
        if not output_file:
            output_file = str(Path(self.config.get(ConfigConstants.CAPTIONS_OUTPUT_DIR)) / f"{video_id}.en.txt")

        # Create output directory if it doesn't exist
        output_dir = Path(output_file).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Dry run
        if dry_run:
            self.dry_run(video_id, output_file)
            return True

        # Check if video exists
        self.logger.info(f"Downloading audio for video ID: {video_id}")
        if self.check_video_exists(video_id):
            try:
                # Download audio using downloadaudio script
                download_audio_script = self.script_dir / "downloadaudio"
                if not download_audio_script.exists():
                    self.logger.error(f"downloadaudio script not found at {download_audio_script}")
                    return False

                result = subprocess.run(
                    [str(download_audio_script), video_id],
                    capture_output=True,
                    text=True,
                    check=True
                )
                audio_file = result.stdout.strip()

                if not audio_file or not Path(audio_file).exists():
                    self.logger.error(f"Failed to download audio for video {video_id}")
                    return False

                self.logger.info(f"Downloaded audio to: {audio_file}")

                # Transcribe audio (with chunking if needed)
                transcription = self.transcribe_audio(audio_file)

                # Save transcription
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(transcription)

                self.logger.info(f"Transcription saved to: {output_file}")

                # Clean up audio file
                try:
                    Path(audio_file).unlink()
                    self.logger.debug(f"Deleted audio file: {audio_file}")
                except OSError as e:
                    self.logger.warning(f"Could not delete audio file {audio_file}: {e}")

                return True

            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to download audio: {e}")
                if e.stderr:
                    self.logger.error(f"Error output: {e.stderr}")
                return False
            except Exception as e:
                self.logger.error(f"Transcription failed: {e}")
                return False
        else:
            self.logger.error(f"Video ID {video_id} is invalid or private")
            return False


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Transcribe YouTube videos using OpenAI Whisper API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s dQw4w9WgXcQ
  %(prog)s -v dQw4w9WgXcQ -o custom_output.txt
        """
    )

    parser.add_argument(
        "video_id",
        help="YouTube video ID"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="Run without making any changes"
    )

    parser.add_argument(
        "-o", "--output",
        help="Specify custom output file path"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}"
    )

    return parser.parse_args()


def main() -> None:
    """Main function."""
    args = parse_args()
    
    # Create transcriber instance
    transcriber = VideoTranscriber()
    
    # Transcribe the video
    success = transcriber.transcribe_video(
        video_id=args.video_id,
        output_file=args.output,
        verbose=args.verbose,
        debug=args.debug,
        dry_run=args.dry_run
    )
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
