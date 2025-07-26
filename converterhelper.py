import os
import subprocess
from configenv import ConfigEnv
from configconstants import ConfigConstants
from loggerutil import LoggerFactory

config = ConfigEnv("config.env")
# Configure logging to stderr
logger = LoggerFactory.get_logger(
    name=os.path.basename(__file__),
    log_to_file=config.get(ConfigConstants.LOGGING, False)
)

def convert_to_jpeg(input_path):
    """Convert image to JPEG using GraphicsMagick.

    Args:
        input_path: Path to input image file

    Returns:
        str: Path to converted JPEG file or None if conversion failed
    """
    try:
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}.jpg"

        # Check if GraphicsMagick is available
        if subprocess.run(["gm", "version"], capture_output=True).returncode != 0:
            logger.warning("GraphicsMagick (gm) not found, skipping conversion")
            return None

        result = subprocess.run(
            ["gm", "convert", input_path, output_path],
            capture_output=True
        )

        if result.returncode == 0:
            print(f"✅ Converted to JPEG: {output_path}")
            # Remove original file if conversion succeeded
            os.remove(input_path)
            return output_path
        else:
            logger.error(f"Conversion failed: {result.stderr.decode().strip()}")
            return None
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        return None
