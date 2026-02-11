"""
Test parsing without score (map + date only)
"""
from pathlib import Path
from native_host import parse_demo_metadata

demo_path = Path("C:/Users/VadimPrivate/Steam/steamapps/common/Counter-Strike Global Offensive/game/csgo/mirage_16-5_18oct2025.dem")

if not demo_path.exists():
    print(f"Demo not found: {demo_path}")
    exit(1)

print(f"Testing new parsing (map + date only)...\n")
print(f"Original: {demo_path.name}")

metadata = parse_demo_metadata(demo_path)

if metadata:
    print(f"\n[SUCCESS] Parsing successful!")
    print(f"  Map: {metadata['map']}")
    print(f"  Date: {metadata['date']}")
    print(f"  New filename: {metadata['filename']}")
    print(f"\nExpected format: mirage_18oct2025.dem")
    print(f"Actual result:   {metadata['filename']}")
else:
    print("[ERROR] Parsing failed!")
