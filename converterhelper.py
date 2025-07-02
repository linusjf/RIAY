import os
import subprocess

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
            print("⚠️ GraphicsMagick (gm) not found, skipping conversion")
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
            print(f"❌ Conversion failed: {result.stderr.decode().strip()}")
            return None
    except Exception as e:
        print(f"❌ Conversion error: {e}")
        return None
