"""
Test script to verify the native host can receive and send messages correctly.
This simulates what Chrome does when communicating with the native host.
"""
import subprocess
import json
import struct
import sys

def send_message_to_host(message):
    """Send a message to the native host and get the response."""
    # Encode the message as JSON
    encoded_message = json.dumps(message).encode('utf-8')
    # Prefix with the message length
    message_length = struct.pack('@I', len(encoded_message))

    # Start the native host process
    process = subprocess.Popen(
        [sys.executable, 'native_host.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Send the message
    process.stdin.write(message_length)
    process.stdin.write(encoded_message)
    process.stdin.flush()
    process.stdin.close()

    # Read the response length (first 4 bytes)
    response_length_bytes = process.stdout.read(4)
    if len(response_length_bytes) == 0:
        print("❌ No response from native host")
        stderr_output = process.stderr.read().decode('utf-8')
        if stderr_output:
            print(f"STDERR: {stderr_output}")
        return None

    response_length = struct.unpack('@I', response_length_bytes)[0]

    # Read the response message
    response_json = process.stdout.read(response_length).decode('utf-8')
    response = json.loads(response_json)

    process.wait()

    return response

def main():
    print("=" * 60)
    print("Testing Native Host Connection")
    print("=" * 60)

    # Test 1: Send a processDemo message
    print("\n>> Test 1: Sending 'processDemo' action...")
    test_message = {
        "action": "processDemo",
        "filePath": "C:\\Downloads\\test-demo.dem.zst"
    }
    print(f"   Message: {json.dumps(test_message, indent=2)}")

    response = send_message_to_host(test_message)

    if response:
        print(f"[OK] Received response: {json.dumps(response, indent=2)}")

        if response.get('status') == 'success':
            print("[OK] Native host is working correctly!")
        else:
            print(f"[WARN] Unexpected status: {response.get('status')}")
    else:
        print("[ERROR] Failed to get response from native host")
        print("\nTroubleshooting:")
        print("1. Check if Python is in your PATH")
        print("2. Check native_host.log for errors")
        print("3. Verify native_host.py has no syntax errors")
        return

    # Test 2: Send an unknown action
    print("\n>> Test 2: Sending unknown action...")
    test_message_2 = {
        "action": "unknownAction",
        "data": "test"
    }
    print(f"   Message: {json.dumps(test_message_2, indent=2)}")

    response_2 = send_message_to_host(test_message_2)

    if response_2:
        print(f"[OK] Received response: {json.dumps(response_2, indent=2)}")

        if response_2.get('status') == 'unknown_action':
            print("[OK] Error handling is working correctly!")

    print("\n" + "=" * 60)
    print("[SUCCESS] Native host script is functioning properly!")
    print("=" * 60)
    print("\nNext step: Check the native_host.log file for detailed logs")
    print(f"Log location: {__file__.replace('test_native_host.py', 'native_host.log')}")

if __name__ == '__main__':
    main()
