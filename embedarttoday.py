#!/usr/bin/env python3
"""Embed artwork image in content for specified day."""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# Constants
VERSION = "1.0.0"
SCRIPT_NAME = Path(__file__).name

# Error codes
E_INVALID_ARGS = 1
E_INVALID_DAY = 2
E_MISSING_TOOLS = 3
E_NO_INTERNET = 4
E_MISSING_ENV = 5
E_MISSING_FILE = 6
E_NO_SATISFACTORY_IMAGES = 7
E_NO_ART_REFERENCED = 8

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(SCRIPT_NAME)

def version() -> None:
    """Print version information."""
    print(VERSION)

def usage(exit_code: int = 0) -> None:
    """Print usage information and exit."""
    output = sys.stdout if exit_code == 0 else sys.stderr
    
    print(f"Usage: {SCRIPT_NAME} <day_number>", file=output)
    print("Embeds artwork image in content for the day.", file=output)
    print("\nArguments:", file=output)
    print("  <day_number> The day number (1-366)", file=output)
    print("\nOptions:", file=output)
    print("  -h, --help     Show this help message", file=output)
    print("  -v, --version  Show version", file=output)
    print("  -d, --debug    Enable debug mode", file=output)
    print("\nExamples:", file=output)
    print(f"  {SCRIPT_NAME} 42", file=output)
    print(f"  {SCRIPT_NAME} 100 --debug", file=output)
    sys.exit(exit_code)

def validate_arguments(args: argparse.Namespace) -> None:
    """Validate command line arguments."""
    if not args.day_number:
        usage(E_INVALID_ARGS)
    
    # TODO: Add day number validation once date utils are available
    # if not date::validate_daynumber(args.day_number, YEAR):
    #     usage(E_INVALID_DAY)

def parse_artdownloader_output(output: str) -> str:
    """Parse artdownloader.py output to find best image."""
    best_selected_image = ""
    
    for line in output.splitlines():
        if "⭐ Best available image (downloaded):" in line:
            parts = line.split(': ')
            best_selected_image = parts[1].split()[0]
        elif "⭐ Best Wikipedia image:" in line:
            parts = line.split(': ')
            best_selected_image = parts[1].split()[0]
    
    return best_selected_image

def verify_image(image_path: str, metadata: Dict[str, str]) -> Dict[str, Union[str, float]]:
    """Verify image using art verifier script."""
    if not image_path:
        logger.error("No image files found to verify")
        return {}
    
    logger.info(f"Verifying image: {image_path}")
    
    try:
        cmd = [
            os.path.join(SCRIPT_DIR, ART_VERIFIER_SCRIPT),
            "--image", image_path,
            "--title", metadata.get("title", ""),
            "--artist", metadata.get("artist", ""),
            "--subject", metadata.get("subject", ""),
            "--location", metadata.get("location", ""),
            "--style", metadata.get("style", ""),
            "--medium", metadata.get("medium", ""),
            "--date", metadata.get("date", "")
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        verification = json.loads(result.stdout)
        
        score = verification.get("cosine_score", 0)
        logger.info(f"Verification passed for: {image_path} (score: {score})")
        
        verification["filename"] = image_path
        return verification
    except subprocess.CalledProcessError:
        logger.error(f"Verification failed for: {image_path}")
        return {}

def generate_markdown(
    caption: str,
    image_path: str,
    source_url: str,
    month: str,
    day_num: int,
    is_stock_image: bool
) -> str:
    """Generate markdown content for artwork."""
    if is_stock_image:
        header = f"### {caption} (Stock Image)"
    else:
        header = f"### {caption}"
    
    # TODO: Implement vidmd::videomarkdown equivalent
    video_md = f"![{caption}]({image_path})\n\n[Source]({source_url})"
    
    return f"\n{header}\n\n{video_md}"

def append_to_day_file(day_num: int, content: str, month: str) -> None:
    """Append content to day's markdown file."""
    day_string = f"Day{day_num:03d}"
    day_file = os.path.join(month, f"{day_string}.md")
    
    if not os.path.exists(day_file):
        logger.error(f"Day file {day_file} does not exist")
        sys.exit(E_MISSING_FILE)
    
    with open(day_file, "a") as f:
        f.write(content)
    logger.info(f"Appended artwork to: {day_file}")

def process_artwork(
    art_details: Dict[str, any],
    month: str,
    day_num: int,
    start_time: float
) -> None:
    """Process single artwork."""
    metadata = {
        "title": art_details.get("details", {}).get("title", "").replace('"', ''),
        "original_title": art_details.get("details", {}).get("original_title", "").replace('"', ''),
        "language": art_details.get("details", {}).get("title_language_iso", "").replace('"', ''),
        "artist": art_details.get("details", {}).get("artist", "").replace('"', ''),
        "location": art_details.get("details", {}).get("location", "").replace('"', ''),
        "date": art_details.get("details", {}).get("date", "").replace('"', ''),
        "style": art_details.get("details", {}).get("style", "").replace('"', ''),
        "medium": art_details.get("details", {}).get("medium", "").replace('"', ''),
        "subject": art_details.get("details", {}).get("subject", "").replace('"', ''),
        "filename": art_details.get("filename", "").replace('"', ''),
        "caption": art_details.get("caption", "").replace('"', '')
    }
    
    try:
        cmd = [
            os.path.join(SCRIPT_DIR, "artdownloader.py"),
            "--filename", metadata["filename"],
            "--title", metadata["title"],
            "--original_title", metadata["original_title"],
            "--language", metadata["language"],
            "--artist", metadata["artist"],
            "--location", metadata["location"],
            "--medium", metadata["medium"],
            "--subject", metadata["subject"],
            "--style", metadata["style"],
            "--date", metadata["date"]
        ]
        
        downloader_output = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
        logger.info(downloader_output)
        
        best_selected_image = parse_artdownloader_output(downloader_output)
        is_stock_image = "best_result" in best_selected_image if best_selected_image else False
        
        if best_selected_image:
            if VERIFY_ART_IMAGES:
                verification = verify_image(best_selected_image, metadata)
                
                if verification.get("image_color", "").lower() in ["grayscale", "black-and-white", "sepia"]:
                    logger.info(f"Image color is {verification['image_color']}")
                
                if verification.get("watermarked", "").lower().startswith("y"):
                    if "wikipedia" not in best_selected_image and "wikimedia" not in best_selected_image:
                        logger.info("Image is watermarked")
                        is_stock_image = True
            
            if IMAGE_CONTENT_VALIDATION == "lenient":
                url_file = f"{os.path.splitext(best_selected_image)[0]}.url.txt"
                source_url = ""
                
                if os.path.exists(url_file):
                    with open(url_file) as f:
                        source_url = f.read().strip()
                else:
                    logger.error("No companion URL file found")
                
                target_dir = os.path.join(month, "jpgs")
                os.makedirs(target_dir, exist_ok=True)
                target_file = os.path.join(target_dir, f"{metadata['filename']}.jpg")
                
                subprocess.run(["cp", best_selected_image, target_file], check=True)
                
                if source_url:
                    with open(os.path.join(target_dir, f"{metadata['filename']}.url.txt"), "w") as f:
                        f.write(source_url)
                
                markdown_content = generate_markdown(
                    metadata["caption"],
                    target_file,
                    source_url,
                    month,
                    day_num,
                    is_stock_image
                )
                append_to_day_file(day_num, markdown_content, month)
            else:
                logger.error("Image content validation policy is set to strict")
        else:
            logger.error("No satisfactory images found via search")
            sys.exit(E_NO_SATISFACTORY_IMAGES)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error processing artwork: {e}")
        sys.exit(E_NO_SATISFACTORY_IMAGES)

def search_database(summary_file: str) -> List[Dict[str, any]]:
    """Search database for art details."""
    try:
        cmd = [os.path.join(SCRIPT_DIR, "locateartforday.py"), summary_file]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        art_details = json.loads(result.stdout)
        
        if not art_details:
            logger.error("No art details found in database")
            sys.exit(E_NO_ART_REFERENCED)
        
        return art_details
    except subprocess.CalledProcessError:
        logger.error("Failed to locate art from database")
        sys.exit(E_NO_ART_REFERENCED)

def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Embed artwork image in content for specified day")
    parser.add_argument("day_number", type=int, help="The day number (1-366)")
    parser.add_argument("-v", "--version", action="store_true", help="Show version")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()
    
    if args.version:
        version()
        sys.exit(0)
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    start_time = time.time()
    validate_arguments(args)
    
    # TODO: Load these from config
    global SCRIPT_DIR, YEAR, ART_DOWNLOADER_DIR, VERIFY_ART_IMAGES, IMAGE_CONTENT_VALIDATION, ART_VERIFIER_SCRIPT
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    YEAR = 2023  # Should come from config
    ART_DOWNLOADER_DIR = ""  # Should come from config
    VERIFY_ART_IMAGES = False  # Should come from config
    IMAGE_CONTENT_VALIDATION = "lenient"  # Should come from config
    ART_VERIFIER_SCRIPT = "verifyartimage.py"  # Should come from config
    
    # TODO: Implement internet check
    
    day_string = f"Day{args.day_number:03d}"
    month = ""  # TODO: Implement month calculation
    
    summary_file = os.path.join(month, f"{day_string}Summary.txt")
    if not os.path.exists(summary_file):
        logger.error(f"Summary file {summary_file} does not exist")
        sys.exit(E_MISSING_FILE)
    
    try:
        # First try extracting from summary file
        extract_cmd = [os.path.join(SCRIPT_DIR, "extractartdetails"), summary_file]
        augment_cmd = [os.path.join(SCRIPT_DIR, "augmentartdetails.py")]
        
        extract_process = subprocess.Popen(extract_cmd, stdout=subprocess.PIPE)
        augment_process = subprocess.Popen(augment_cmd, stdin=extract_process.stdout, stdout=subprocess.PIPE)
        extract_process.stdout.close()
        
        output = augment_process.communicate()[0].decode()
        art_details_array = json.loads(output)
        
        if not art_details_array:
            logger.warning("No art details found in summary")
            logger.info("Locating matching art from existing database...")
            art_details_array = search_database(summary_file)
        
        for art_details in art_details_array:
            process_artwork(art_details, month, args.day_number, start_time)
        
        # TODO: Implement genmonth and stitch commands
        subprocess.run([os.path.join(SCRIPT_DIR, "genmonth"), month], check=True)
        subprocess.run([os.path.join(SCRIPT_DIR, "stitch")], check=True)
        
        runtime = time.time() - start_time
        logger.info(f"Completed in {runtime:.2f} seconds")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to process artwork: {e}")
        sys.exit(E_NO_ART_REFERENCED)

if __name__ == "__main__":
    main()
