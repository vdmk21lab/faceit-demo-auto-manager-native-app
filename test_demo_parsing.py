"""
Test script to parse CS2 demo file and extract metadata
"""
import sys
import time
from pathlib import Path
from datetime import datetime

try:
    from demoparser2 import DemoParser
except ImportError:
    print("[ERROR] demoparser2 not installed. Run: pip install demoparser2")
    sys.exit(1)

def parse_demo_full(demo_path: Path) -> dict:
    """
    Full parsing - header + rounds
    Returns: map name + score + date
    """
    print(f"\n[INFO] Parsing demo: {demo_path.name}")
    print(f"[INFO] File size: {demo_path.stat().st_size / 1024 / 1024:.1f} MB")

    start_time = time.time()

    try:
        parser = DemoParser(str(demo_path))

        # Parse header
        print("[INFO] Parsing header...")
        header_start = time.time()
        header = parser.parse_header()
        header_time = time.time() - header_start

        print(f"[OK] Header parsed in {header_time:.3f}s")
        print(f"     Map: {header.get('map_name', 'unknown')}")

        # Clean map name (remove de_ or cs_ prefix)
        map_name = header.get('map_name', 'unknown')
        map_name = map_name.replace('de_', '').replace('cs_', '')

        # Parse rounds to get score
        print("[INFO] Parsing rounds...")
        rounds_start = time.time()

        # Parse round_end events with winner column
        df = parser.parse_event("round_end")

        rounds_time = time.time() - rounds_start
        print(f"[OK] Rounds parsed in {rounds_time:.3f}s")
        print(f"     Total rounds: {len(df)}")

        # Calculate final score
        ct_wins = int((df['winner'] == 'CT').sum())
        t_wins = int((df['winner'] == 'T').sum())

        print(f"     CT wins: {ct_wins}")
        print(f"     T wins: {t_wins}")

        # Format score (winner first)
        if ct_wins > t_wins:
            score = f"{ct_wins}-{t_wins}"
        else:
            score = f"{t_wins}-{ct_wins}"

        # Get date from file modification time
        file_date = datetime.fromtimestamp(demo_path.stat().st_mtime)
        date_str = file_date.strftime("%d%b%Y").lower()

        total_time = time.time() - start_time

        result = {
            'map': map_name,
            'score': score,
            'date': date_str,
            'filename': f"{map_name}_{score}_{date_str}.dem",
            'parse_time': total_time,
            'header_time': header_time,
            'rounds_time': rounds_time
        }

        print(f"\n[SUCCESS] Parsing completed in {total_time:.3f}s")
        print(f"[INFO] New filename: {result['filename']}")

        return result

    except Exception as e:
        print(f"[ERROR] Parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    # Try to find the demo file
    # User said it's in csgo directory: 1-b1654204-9254-467a-8cd2-fdc902940515-1-1.dem

    # Try common CS2 paths
    potential_paths = [
        Path("C:/Users/VadimPrivate/Steam/steamapps/common/Counter-Strike Global Offensive/game/csgo/1-b1654204-9254-467a-8cd2-fdc902940515-1-1.dem"),
        Path("C:/Program Files (x86)/Steam/steamapps/common/Counter-Strike Global Offensive/game/csgo/1-b1654204-9254-467a-8cd2-fdc902940515-1-1.dem"),
        Path("D:/Steam/steamapps/common/Counter-Strike Global Offensive/game/csgo/1-b1654204-9254-467a-8cd2-fdc902940515-1-1.dem"),
    ]

    # Also check if path provided as argument
    if len(sys.argv) > 1:
        potential_paths.insert(0, Path(sys.argv[1]))

    demo_path = None
    for path in potential_paths:
        if path.exists():
            demo_path = path
            break

    if not demo_path:
        print("[ERROR] Demo file not found!")
        print("[INFO] Tried:")
        for path in potential_paths:
            print(f"  - {path}")
        print(f"\n[INFO] Usage: python {Path(__file__).name} <path-to-demo.dem>")
        sys.exit(1)

    # Parse the demo
    result = parse_demo_full(demo_path)

    if result:
        print("\n" + "="*60)
        print("PARSING RESULTS")
        print("="*60)
        print(f"Map:          {result['map']}")
        print(f"Score:        {result['score']}")
        print(f"Date:         {result['date']}")
        print(f"New filename: {result['filename']}")
        print(f"\nPerformance:")
        print(f"  Header:     {result['header_time']:.3f}s")
        print(f"  Rounds:     {result['rounds_time']:.3f}s")
        print(f"  Total:      {result['parse_time']:.3f}s")
        print("="*60)

if __name__ == '__main__':
    main()
