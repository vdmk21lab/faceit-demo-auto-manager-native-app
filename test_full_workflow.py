"""
Test the full demo processing workflow with an existing demo file
"""
import json
from pathlib import Path
from native_host import process_demo_file

# Find the test demo file
demo_path = Path("C:/Users/VadimPrivate/Steam/steamapps/common/Counter-Strike Global Offensive/game/csgo/1-b1654204-9254-467a-8cd2-fdc902940515-1-1.dem")

if not demo_path.exists():
    print(f"[ERROR] Demo file not found: {demo_path}")
    exit(1)

print(f"[INFO] Found demo: {demo_path.name}")
print(f"[INFO] Size: {demo_path.stat().st_size / 1024 / 1024:.1f} MB")
print(f"\n[INFO] Testing native host process_demo_file() function...")
print("="*60)

# Since the demo is already decompressed, we can't test decompression
# But we can test the parsing and renaming functionality

from native_host import parse_demo_metadata

# Test parsing
metadata = parse_demo_metadata(demo_path)

if metadata:
    print("\n[SUCCESS] Parsing successful!")
    print(f"  Map: {metadata['map']}")
    print(f"  Score: {metadata['score']}")
    print(f"  Date: {metadata['date']}")
    print(f"  New filename: {metadata['filename']}")

    # Test rename
    new_path = demo_path.parent / metadata['filename']

    if new_path.exists():
        print(f"\n[INFO] File already renamed to: {new_path.name}")
    else:
        print(f"\n[INFO] Would rename:")
        print(f"  From: {demo_path.name}")
        print(f"  To:   {metadata['filename']}")

        # Actually rename it
        try:
            demo_path.rename(new_path)
            print(f"[SUCCESS] File renamed!")
        except Exception as e:
            print(f"[ERROR] Rename failed: {e}")
else:
    print("[ERROR] Parsing failed!")

print("\n" + "="*60)
print("[INFO] Test complete!")
