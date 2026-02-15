import sys
import json
import struct
import logging
from pathlib import Path

try:
    import zstandard as zstd
    ZSTD_AVAILABLE = True
except ImportError:
    ZSTD_AVAILABLE = False
    logging.warning("zstandard module not available. Install with: pip install zstandard")

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False
    logging.warning("pyperclip module not available. Install with: pip install pyperclip")

try:
    from demoparser2 import DemoParser
    DEMOPARSER_AVAILABLE = True
except ImportError:
    DEMOPARSER_AVAILABLE = False
    logging.warning("demoparser2 module not available. Install with: pip install demoparser2")

from datetime import datetime
from path_finder import PathConfigManager

def get_executable_dir():
    """
    Get the directory where the executable/script is located.
    Works for both .py script and .exe (compiled with PyInstaller).
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled .exe (frozen by PyInstaller)
        return Path(sys.executable).parent
    else:
        # Running as .py script
        return Path(__file__).parent

# Set up logging to a file in the same directory as the script/exe.
# This is crucial for debugging because stdout is reserved for Chrome communication.
logging.basicConfig(
    filename=str(get_executable_dir() / 'native_host.log'),
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    filemode='a',  # Append to the log file
    encoding='utf-8'
)

def get_message():
    """
    Reads a message from stdin, adhering to the Native Messaging protocol.
    The first 4 bytes define the message length in native byte order.
    """
    raw_length = sys.stdin.buffer.read(4)
    if not raw_length:
        logging.info("No message length received. Exiting.")
        sys.exit(0)

    message_length = struct.unpack('@I', raw_length)[0]
    message = sys.stdin.buffer.read(message_length).decode('utf-8')
    logging.info(f"Received message of length {message_length}: {message}")
    return json.loads(message)

def send_message(message_content):
    """
    Sends a message to stdout, adhering to the Native Messaging protocol.
    The message is a JSON-encoded string, prefixed with its length in bytes.
    """
    encoded_content = json.dumps(message_content).encode('utf-8')
    encoded_length = struct.pack('@I', len(encoded_content))

    logging.info(f"Sending response: {encoded_content.decode('utf-8')}")

    sys.stdout.buffer.write(encoded_length)
    sys.stdout.buffer.write(encoded_content)
    sys.stdout.buffer.flush()

def copy_playdemo_to_clipboard(demo_filename: str) -> dict:
    """
    Copy playdemo command to clipboard (no CS2 launching).

    Args:
        demo_filename: Name of the demo file (without path)

    Returns:
        dict: Status of the clipboard operation
    """
    playdemo_command = f"playdemo {demo_filename}"

    logging.info(f"Copying command to clipboard: {playdemo_command}")

    try:
        if CLIPBOARD_AVAILABLE:
            pyperclip.copy(playdemo_command)
            logging.info(f"Successfully copied to clipboard: {playdemo_command}")
            return {
                "method": "clipboard",
                "command": playdemo_command,
                "message": f"Command copied to clipboard: {playdemo_command}"
            }
        else:
            logging.warning("pyperclip not available")
            return {
                "method": "manual",
                "command": playdemo_command,
                "message": f"Clipboard unavailable. Manual command: {playdemo_command}"
            }
    except Exception as e:
        logging.error(f"Failed to copy to clipboard: {e}")
        return {
            "method": "error",
            "command": playdemo_command,
            "message": f"Clipboard error: {str(e)}"
        }

def delete_demo_file(demo_filename: str) -> dict:
    """
    Delete a demo file from the CS2 csgo folder.

    Args:
        demo_filename: Name of the demo file to delete (e.g., "nuke_08feb2026.dem")

    Returns:
        dict: Status of the deletion
    """
    try:
        config_manager = PathConfigManager()
        csgo_folder = config_manager.get_cs2_csgo_path()

        if not csgo_folder:
            logging.error("CS2 csgo folder not found")
            return {
                "status": "error",
                "message": "CS2 installation not found."
            }

        demo_path = csgo_folder / demo_filename

        if not demo_path.exists():
            logging.warning(f"Demo file not found: {demo_path}")
            return {
                "status": "error",
                "message": f"Demo file not found: {demo_filename}"
            }

        # Delete the file
        demo_path.unlink()
        logging.info(f"Successfully deleted demo file: {demo_path}")

        return {
            "status": "success",
            "message": f"Demo file deleted: {demo_filename}"
        }

    except Exception as e:
        logging.error(f"Error deleting demo file: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to delete demo: {str(e)}"
        }

def parse_demo_metadata(demo_path: Path) -> dict:
    """
    Parse demo file and extract metadata: map name and date.

    Args:
        demo_path: Path to the .dem file

    Returns:
        dict with 'map', 'date', and 'filename' keys
        Returns None if parsing fails
    """
    if not DEMOPARSER_AVAILABLE:
        logging.warning("demoparser2 not available, skipping demo parsing")
        return None

    try:
        logging.info(f"Parsing demo metadata: {demo_path.name}")

        parser = DemoParser(str(demo_path))

        # Parse header for map name
        header = parser.parse_header()
        map_name = header.get('map_name', 'unknown')

        # Clean map name (remove de_ or cs_ prefix)
        map_name = map_name.replace('de_', '').replace('cs_', '')
        logging.info(f"Map: {map_name}")

        # Get date from file modification time
        file_date = datetime.fromtimestamp(demo_path.stat().st_mtime)
        date_str = file_date.strftime("%d%b%Y").lower()  # e.g., "19oct2025"

        # Create base filename (map + date)
        base_filename = f"{map_name}_{date_str}"
        new_filename = f"{base_filename}.dem"

        # Check if file already exists, add counter if needed
        counter = 2
        while (demo_path.parent / new_filename).exists() and str(demo_path.parent / new_filename) != str(demo_path):
            new_filename = f"{base_filename}_{counter}.dem"
            counter += 1

        logging.info(f"Parsed demo metadata - New filename: {new_filename}")

        return {
            'map': map_name,
            'date': date_str,
            'filename': new_filename
        }

    except Exception as e:
        logging.error(f"Failed to parse demo metadata: {e}", exc_info=True)
        return None

def process_demo_file(file_path_str: str) -> dict:
    """
    Process a FACEIT demo file: decompress, move to CS2 csgo folder, and launch.

    Args:
        file_path_str: Full path to the downloaded .dem.zst file

    Returns:
        dict: Status and details about the processing
    """
    try:
        # Check if zstandard is available
        if not ZSTD_AVAILABLE:
            return {
                "status": "error",
                "message": "Decompression library not installed. Please run: pip install zstandard"
            }

        file_path = Path(file_path_str)

        # Verify file exists
        if not file_path.exists():
            logging.error(f"File not found: {file_path}")
            return {
                "status": "error",
                "message": f"File not found: {file_path}"
            }

        # Verify it's a .zst file
        if file_path.suffix != '.zst':
            logging.error(f"File is not a .zst file: {file_path}")
            return {
                "status": "error",
                "message": "File is not a compressed demo (.zst)"
            }

        logging.info(f"Processing demo file: {file_path}")

        # Get CS2 csgo folder
        config_manager = PathConfigManager()
        csgo_folder = config_manager.get_cs2_csgo_path()

        if not csgo_folder:
            logging.error("CS2 csgo folder not found")
            return {
                "status": "error",
                "message": "CS2 installation not found. Please configure the CS2 folder path manually.",
                "action_required": "configure_path"
            }

        logging.info(f"Using CS2 csgo folder: {csgo_folder}")

        # Decompress directly to CS2 csgo folder
        output_filename = file_path.stem  # Removes .zst extension
        output_path = csgo_folder / output_filename

        logging.info(f"Decompressing to: {output_path}")

        # Decompress the file
        with open(file_path, 'rb') as compressed:
            dctx = zstd.ZstdDecompressor()
            with open(output_path, 'wb') as destination:
                dctx.copy_stream(compressed, destination)

        # Verify decompressed file exists
        if not output_path.exists():
            logging.error("Decompression failed - output file not created")
            return {
                "status": "error",
                "message": "Decompression failed - output file not created"
            }

        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        logging.info(f"Successfully decompressed: {output_path} ({file_size_mb:.1f} MB)")

        # Delete the original compressed file
        try:
            file_path.unlink()
            logging.info(f"Deleted original compressed file: {file_path}")
        except Exception as e:
            logging.warning(f"Could not delete original file: {e}")

        # Parse demo metadata and rename file
        final_filename = output_filename  # Default to original name
        demo_metadata = parse_demo_metadata(output_path)

        if demo_metadata:
            # Rename file with metadata
            new_filename = demo_metadata['filename']
            new_path = csgo_folder / new_filename

            try:
                output_path.rename(new_path)
                logging.info(f"Renamed: {output_filename} → {new_filename}")
                output_path = new_path  # Update path reference
                final_filename = new_filename
            except Exception as e:
                logging.warning(f"Failed to rename file: {e}")
                # Continue with original filename
        else:
            logging.info("Skipping demo rename (parsing failed or unavailable)")

        # Copy playdemo command to clipboard
        clipboard_result = copy_playdemo_to_clipboard(final_filename)

        # Build response with metadata
        response = {
            "status": "success",
            "message": f"Demo ready! ({file_size_mb:.1f} MB)",
            "demo_name": final_filename,
            "output_path": str(output_path),
            "csgo_folder": str(csgo_folder),
            "clipboard": clipboard_result
        }

        # Add metadata if available
        if demo_metadata:
            response["metadata"] = {
                "map": demo_metadata['map'],
                "date": demo_metadata['date'],
                "renamed": True
            }
        else:
            response["metadata"] = {"renamed": False}

        return response

    except Exception as e:
        logging.error(f"Error processing demo: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Processing failed: {str(e)}"
        }

def main():
    """
    Main function to read a single message and send a single response.
    """
    try:
        received_message = get_message()

        # Check for the specific action requested by the Chrome extension
        if received_message.get("action") == "processDemo":
            file_path = received_message.get("filePath")
            logging.info(f"Action 'processDemo' received for file: {file_path}")

            # Process the demo file
            result = process_demo_file(file_path)

            # Send result back to extension
            send_message(result)

        elif received_message.get("action") == "getCS2Path":
            # Allow extension to query for CS2 path
            logging.info("Action 'getCS2Path' received")
            config_manager = PathConfigManager()
            paths = config_manager.get_all_detected_paths()
            send_message({"status": "success", "paths": paths})

        elif received_message.get("action") == "setCS2Path":
            # Allow extension to set custom CS2 path
            custom_path = received_message.get("path")
            logging.info(f"Action 'setCS2Path' received with path: {custom_path}")

            config_manager = PathConfigManager()
            if config_manager.set_custom_path(custom_path):
                send_message({"status": "success", "message": "Custom path set successfully"})
            else:
                send_message({"status": "error", "message": "Invalid path or path does not exist"})

        elif received_message.get("action") == "deleteDemo":
            # Delete demo file from CS2 csgo folder
            demo_filename = received_message.get("demoName")
            logging.info(f"Action 'deleteDemo' received for file: {demo_filename}")

            # Delete the demo file
            result = delete_demo_file(demo_filename)

            # Send result back to extension
            send_message(result)

        elif received_message.get("action") == "ping":
            # Health check to verify native host is running
            logging.info("Action 'ping' received - native host is alive")
            send_message({"status": "success", "message": "pong"})

        else:
            # Handle any unknown actions
            logging.warning(f"Received unknown action: {received_message.get('action')}")
            send_message({"status": "unknown_action", "received": received_message})

    except Exception as e:
        # Log any exceptions to the file for debugging
        logging.error(f"An error occurred: {e}", exc_info=True)
        # Attempt to send an error response back to the extension if possible
        try:
            send_message({"status": "error", "message": str(e)})
        except Exception as send_e:
            logging.error(f"Failed to send error message back to extension: {send_e}")

if __name__ == '__main__':
    logging.info("Native host script started.")
    main()
    logging.info("Native host script finished.")
