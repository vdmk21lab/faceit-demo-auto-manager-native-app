"""
Debug script to see what fields are available in round_end events
"""
import sys
from pathlib import Path
from demoparser2 import DemoParser

demo_path = Path("C:/Users/VadimPrivate/Steam/steamapps/common/Counter-Strike Global Offensive/game/csgo/1-b1654204-9254-467a-8cd2-fdc902940515-1-1.dem")

if not demo_path.exists():
    print(f"Demo not found: {demo_path}")
    sys.exit(1)

print(f"Parsing: {demo_path.name}\n")

parser = DemoParser(str(demo_path))

# Parse round_end events with ALL available fields
print("Parsing round_end events...")
df = parser.parse_event("round_end")

print(f"\nTotal rounds: {len(df)}")
print(f"\nAvailable columns:")
for col in df.columns:
    print(f"  - {col}")

# Show first few rows
print(f"\nFirst 3 rows:")
print(df.head(3))

# Try to find winner-related columns
winner_cols = [col for col in df.columns if 'win' in col.lower() or 'winner' in col.lower() or 'team' in col.lower() or 'score' in col.lower()]
if winner_cols:
    print(f"\nWinner-related columns: {winner_cols}")
    print(df[winner_cols].head(10))
