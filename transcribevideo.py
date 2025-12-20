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
import tempfile
from pathlib import Path
import urllib.request
import urllib.error
from typing import List, Tuple

# Add the script directory to the path to import local modules
SCRIPT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(SCRIPT_DIR))


# Import ConfigEnv and ConfigConstants
try:
    from configenv import ConfigEnv
    from configconstants import ConfigConstants
except ImportError:
    # Add parent directory to path for direct imports
    sys.path.insert(0, str(SCRIPT_DIR.parent))
    from configenv import ConfigEnv
    from configconstants import ConfigConstants

VERSION = "1.0.0"
SCRIPT_NAME = Path(__file__).name
FASTER_WHISPER = "faster-whisper"
MAX_CHUNK_DURATION = 600  # 10 minutes in seconds

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def is_package_installed(package_name: str) -> bool:
    """Check if a Python package is installed."""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False


def check_video_exists(video_id: str) -> bool:
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
                logger.debug(f"Video {video_id} exists and is accessible")
                return True
        except urllib.error.HTTPError as e:
            # 404 means video doesn't exist or is private
            if e.code == 404:
                logger.debug(f"Video {video_id} not found (404)")
                return False
            # Other HTTP errors might indicate temporary issues
            logger.warning(f"HTTP error checking video {video_id}: {e.code}")
            # For other errors, we'll still try to download (might be temporary)
            return True
        except urllib.error.URLError as e:
            logger.warning(f"URL error checking video {video_id}: {e.reason}")
            # Network issues - we'll still try to download
            return True

        return False
    except Exception as e:
        logger.warning(f"Error checking if video {video_id} exists: {e}")
        # If the check fails for any reason, we'll still try to download
        # and let the download process fail if the video truly doesn't exist
        return True


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


def check_local_prerequisites() -> bool:
    """Check if local transcription prerequisites are available."""
    try:
        # Check for ffmpeg
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        # Check for whisper command
        subprocess.run(["whisper", "--help"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_audio_duration(audio_file: str) -> float:
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
        logger.info(f"Audio file duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
        return duration
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError) as e:
        logger.error(f"Failed to get audio duration: {e}")
        raise RuntimeError(f"Could not determine audio file duration: {e}")


def split_audio_file(audio_file: str, chunk_duration: int = MAX_CHUNK_DURATION) -> List[str]:
    """
    Split audio file into chunks of specified duration.
    Returns list of chunk file paths.
    """
    try:
        # Get total duration
        total_duration = get_audio_duration(audio_file)
        
        # Calculate number of chunks needed
        num_chunks = int(total_duration // chunk_duration) + (1 if total_duration % chunk_duration > 0 else 0)
        
        if num_chunks <= 1:
            logger.info(f"Audio file is {total_duration/60:.2f} minutes, no splitting needed")
            return [audio_file]
        
        logger.info(f"Splitting {total_duration/60:.2f} minute audio into {num_chunks} chunks")
        
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
            
            logger.debug(f"Creating chunk {i+1}/{num_chunks}: {chunk_filename}")
            subprocess.run(cmd, capture_output=True, check=True)
            chunk_files.append(str(chunk_file))
        
        logger.info(f"Created {len(chunk_files)} chunk files")
        return chunk_files
        
    except Exception as e:
        logger.error(f"Failed to split audio file: {e}")
        raise


def transcribe_via_openai_api(audio_file: str, config: ConfigEnv) -> str:
    """Transcribe audio using OpenAI Whisper API directly."""
    try:
        # Import OpenAI client
        from openai import OpenAI

        # Get base URL and endpoint from config
        base_url = config.get(ConfigConstants.ASR_LLM_BASE_URL)

        if not base_url:
            logger.error("ASR_LLM_BASE_URL not configured")
            raise ValueError("ASR_LLM_BASE_URL not configured")

        full_url = base_url

        logger.info(f"Transcribing with OpenAI Whisper API using endpoint: {full_url}")

        # Initialize OpenAI client with API key and custom base URL
        client = OpenAI(
            api_key=config.get(ConfigConstants.ASR_LLM_API_KEY),
            base_url=full_url
        )

        # Open the audio file
        with open(audio_file, 'rb') as audio:
            # Call the OpenAI Whisper API
            response = client.audio.transcriptions.create(
                model=config.get(ConfigConstants.ASR_LLM_MODEL),
                file=audio,
                response_format="text",
                prompt=config.get(ConfigConstants.ASR_INITIAL_PROMPT, ''),
                language="en"
            )

        # The response is already text when response_format="text"
        return response

    except ImportError:
        logger.error("OpenAI Python library not installed. Install with: pip install openai")
        raise
    except Exception as e:
        logger.error(f"OpenAI API transcription failed: {e}")
        raise


def transcribe_locally(audio_file: str, config: ConfigEnv) -> str:
    """Transcribe audio using local installation."""
    if config.get(ConfigConstants.USE_FASTER_WHISPER, False):
        try:
            if is_package_installed(FASTER_WHISPER):
                # Run fasterwhisperer.py script
                result = subprocess.run(
                    [sys.executable, str(SCRIPT_DIR / "fasterwhisperer.py"), audio_file],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return result.stdout
            else:
                logger.error(f"Python package {FASTER_WHISPER} not available")
                raise RuntimeError(f"Package {FASTER_WHISPER} not installed")
        except Exception as e:
            logger.error(f"Faster whisper transcription failed: {e}")
            raise
    else:
        if check_local_prerequisites():
            try:
                cmd = [
                    "whisper",
                    "--task", "transcribe",
                    "--model", config.get(ConfigConstants.ASR_LOCAL_MODEL, 'base'),
                    "--output_format", "txt",
                    "--language", "en",
                    "--initial_prompt", config.get(ConfigConstants.ASR_INITIAL_PROMPT, ''),
                    "--carry_initial_propmt", str(config.get(ConfigConstants.ASR_CARRY_INITIAL_PROMPT, 'false')).lower(),
                    "--beam_size", str(config.get(ConfigConstants.ASR_BEAM_SIZE, 5)),
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
                logger.error(f"Local whisper transcription failed: {e}")
                raise
        else:
            logger.error("ffmpeg and/or whisper not available")
            raise RuntimeError("Local transcription prerequisites not met")


def transcribe_audio_chunks(audio_file: str, config: ConfigEnv) -> str:
    """Transcribe audio file, splitting into chunks if longer than MAX_CHUNK_DURATION."""
    logger.info("Transcribing with Whisper...")
    start_time = time.time()
    
    try:
        # Check if we should use local transcription
        use_local = config.get(ConfigConstants.TRANSCRIBE_LOCALLY, False)
        
        # Get audio duration and split if needed
        try:
            duration = get_audio_duration(audio_file)
            if duration > MAX_CHUNK_DURATION:
                logger.info(f"Audio file is {duration/60:.2f} minutes, splitting into chunks")
                chunk_files = split_audio_file(audio_file)
                
                # Transcribe each chunk
                all_transcripts = []
                for i, chunk_file in enumerate(chunk_files):
                    logger.info(f"Transcribing chunk {i+1}/{len(chunk_files)}")
                    
                    if use_local:
                        chunk_transcript = transcribe_locally(chunk_file, config)
                    else:
                        chunk_transcript = transcribe_via_openai_api(chunk_file, config)
                    
                    all_transcripts.append(chunk_transcript)
                    
                    # Clean up chunk file
                    try:
                        Path(chunk_file).unlink()
                        logger.debug(f"Deleted chunk file: {chunk_file}")
                    except OSError as e:
                        logger.warning(f"Could not delete chunk file {chunk_file}: {e}")
                
                # Combine all transcripts
                combined_transcript = "\n\n".join(all_transcripts)
                logger.info(f"Combined {len(chunk_files)} chunks into final transcript")
                
                duration = time.time() - start_time
                logger.info(f"Transcribed video in {duration:.2f} seconds")
                return combined_transcript
            else:
                # File is short enough, transcribe normally
                logger.info(f"Audio file is {duration/60:.2f} minutes, transcribing as single file")
                if use_local:
                    return transcribe_locally(audio_file, config)
                else:
                    return transcribe_via_openai_api(audio_file, config)
                    
        except Exception as e:
            logger.error(f"Failed to process audio file: {e}")
            raise
            
    except Exception as e:
        # Handle failover mode for API transcription
        if not use_local and config.get(ConfigConstants.ENABLE_FAILOVER_MODE, True):
            logger.warning(f"Chunked transcription failed: {e}. Trying single file transcription...")
            try:
                if use_local:
                    return transcribe_locally(audio_file, config)
                else:
                    return transcribe_via_openai_api(audio_file, config)
            except Exception as e2:
                logger.error(f"Fallback transcription also failed: {e2}")
                raise
        else:
            raise


def transcribe_audio(audio_file: str, config: ConfigEnv) -> str:
    """Transcribe audio file using appropriate method (wrapper for backward compatibility)."""
    return transcribe_audio_chunks(audio_file, config)


def dry_run(video_id: str, output_file: str, config: ConfigEnv) -> None:
    """Perform dry run without actual processing."""
    logger.info(f"DRY RUN: Would process video ID: {video_id}")
    logger.info(f"DRY RUN: Would create output file: {output_file}")
    logger.info("DRY RUN: Would download audio using downloadaudio script")
    logger.info("DRY RUN: Would check audio duration and split if > 10 minutes")
    logger.info("DRY RUN: Would transcribe and/or translate audio using Whisper API")
    logger.info("DRY RUN: Would clean up temporary files")


def main() -> None:
    """Main function."""
    args = parse_args()

    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    # Load configuration using ConfigEnv
    config_path = SCRIPT_DIR / "config.env"
    config = ConfigEnv(str(config_path),override=True, include_os_env=True)

    # Check required environment variables using ConfigConstants
    required_vars = [
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

    for var in required_vars:
        if config.get(var) is None:
            logger.error(f"Required configuration variable not found: {var}")
            sys.exit(1)

    # Determine output file
    if args.output:
        output_file = args.output
    else:
        output_file = str(Path(config.get(ConfigConstants.CAPTIONS_OUTPUT_DIR)) / f"{args.video_id}.en.txt")

    # Create output directory if it doesn't exist
    output_dir = Path(output_file).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Dry run
    if args.dry_run:
        dry_run(args.video_id, output_file, config)
        return

    # Check if video exists
    logger.info(f"Downloading audio for video ID: {args.video_id}")
    if check_video_exists(args.video_id):
        try:
            # Download audio using downloadaudio script
            download_audio_script = SCRIPT_DIR / "downloadaudio"
            if not download_audio_script.exists():
                logger.error(f"downloadaudio script not found at {download_audio_script}")
                sys.exit(1)

            result = subprocess.run(
                [str(download_audio_script), args.video_id],
                capture_output=True,
                text=True,
                check=True
            )
            audio_file = result.stdout.strip()

            if not audio_file or not Path(audio_file).exists():
                logger.error(f"Failed to download audio for video {args.video_id}")
                sys.exit(1)

            logger.info(f"Downloaded audio to: {audio_file}")

            # Transcribe audio (with chunking if needed)
            transcription = transcribe_audio(audio_file, config)

            # Save transcription
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(transcription)

            logger.info(f"Transcription saved to: {output_file}")

            # Clean up audio file
            try:
                Path(audio_file).unlink()
                logger.debug(f"Deleted audio file: {audio_file}")
            except OSError as e:
                logger.warning(f"Could not delete audio file {audio_file}: {e}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to download audio: {e}")
            if e.stderr:
                logger.error(f"Error output: {e.stderr}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            sys.exit(1)
    else:
        logger.error(f"Video ID {args.video_id} is invalid or private")
        sys.exit(1)


if __name__ == "__main__":
    main()
