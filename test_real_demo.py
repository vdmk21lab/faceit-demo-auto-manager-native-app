"""Test processing a real FACEIT demo file"""
import subprocess
import json
import struct
import sys
from pathlib import Path

def test_demo_processing(demo_file_path):
    """Test the native host with a real demo file"""
    demo_path = Path(demo_file_path)

    if not demo_path.exists():
        print(f"[ERROR] Demo file not found: {demo_path}")
        return

    print("=" * 60)
    print("Testing Demo Processing")
    print("=" * 60)
    print(f"\nDemo file: {demo_path}")
    print(f"File size: {demo_path.stat().st_size / (1024 * 1024):.1f} MB")

    # Prepare message
    message = {
        "action": "processDemo",
        "filePath": str(demo_path)
    }

    encoded = json.dumps(message).encode('utf-8')
    msg_with_length = struct.pack('@I', len(encoded)) + encoded

    print(f"\n[1] Sending message to native host...")
    print(f"    Action: {message['action']}")

    # Run native host
    process = subprocess.Popen(
        [sys.executable, 'native_host.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = process.communicate(input=msg_with_length, timeout=30)

    if stderr:
        print(f"\n[WARN] STDERR: {stderr.decode('utf-8')}")

    print("\n[2] Receiving response...")

    if len(stdout) >= 4:
        response_length = struct.unpack('@I', stdout[:4])[0]
        response_json = stdout[4:4+response_length].decode('utf-8')
        response = json.loads(response_json)

        print(f"\n[3] Response received:")
        print(json.dumps(response, indent=2))

        if response.get('status') == 'success':
            print("\n" + "=" * 60)
            print("[SUCCESS] Demo processed successfully!")
            print("=" * 60)
            print(f"\nDemo name: {response.get('demo_name')}")
            print(f"Output path: {response.get('output_path')}")
            print(f"Message: {response.get('message')}")

            # Verify output file exists
            output_path = Path(response.get('output_path'))
            if output_path.exists():
                print(f"\n[OK] Demo file verified: {output_path}")
                print(f"     Size: {output_path.stat().st_size / (1024 * 1024):.1f} MB")
            else:
                print(f"\n[ERROR] Demo file not found at: {output_path}")

        elif response.get('status') == 'error':
            print("\n" + "=" * 60)
            print("[ERROR] Demo processing failed!")
            print("=" * 60)
            print(f"\nError: {response.get('message')}")

            if response.get('action_required') == 'configure_path':
                print("\n[ACTION REQUIRED] CS2 path not auto-detected.")
                print("You need to configure the CS2 replays folder manually.")

    else:
        print("[ERROR] No response received from native host")

    print("\n" + "=" * 60)
    print("Check native_host.log for detailed logs")
    print("=" * 60)


if __name__ == '__main__':
    # Test with the actual downloaded file
    demo_file = r"C:\Users\VadimPrivate\Downloads\1-b1654204-9254-467a-8cd2-fdc902940515-1-1.dem.zst"

    # Check if file still exists
    if not Path(demo_file).exists():
        print(f"Demo file not found: {demo_file}")
        print("Please download a FACEIT demo first or specify a different file.")
        print("\nUsage: python test_real_demo.py")
        print("Edit the 'demo_file' variable in the script to point to your .dem.zst file")
    else:
        test_demo_processing(demo_file)
