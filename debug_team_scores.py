"""
Try to get team scores from game state
"""
from pathlib import Path
from demoparser2 import DemoParser

demo_path = Path("C:/Users/VadimPrivate/Steam/steamapps/common/Counter-Strike Global Offensive/game/csgo/mirage_16-5_18oct2025.dem")

if not demo_path.exists():
    print(f"Demo not found: {demo_path}")
    exit(1)

print(f"Parsing: {demo_path.name}\n")

parser = DemoParser(str(demo_path))

# Try to parse game state with team information
print("Trying to parse with various team/score fields...\n")

try:
    # Parse just ticks to see what game state fields are available
    df = parser.parse_ticks(["m_iMatchStats_PlayersAlive_CT", "m_iMatchStats_PlayersAlive_T"])

    print("Parsing ticks succeeded!")
    print(f"Available fields: {df.columns.tolist()}")
except Exception as e:
    print(f"Parsing ticks failed: {e}")

# Try parsing rounds with different approach
print("\nTrying round_officially_ended event...")
try:
    df_official = parser.parse_event("round_officially_ended")
    print(f"Found {len(df_official)} round_officially_ended events")
    if len(df_official) > 0:
        print(f"Columns: {df_official.columns.tolist()}")
        print(f"\nFirst 5 rows:")
        print(df_official.head())
except Exception as e:
    print(f"Failed: {e}")

# Try getting header with team info
print("\nChecking header for team names...")
header = parser.parse_header()
print(f"Header keys: {header.keys()}")
if 'team_name_t' in header or 'team_name_ct' in header:
    print(f"Team names found!")
    print(f"  T side: {header.get('team_name_t', 'N/A')}")
    print(f"  CT side: {header.get('team_name_ct', 'N/A')}")
