"""
Debug script to see ALL rounds and their winners
"""
from pathlib import Path
from demoparser2 import DemoParser

demo_path = Path("C:/Users/VadimPrivate/Steam/steamapps/common/Counter-Strike Global Offensive/game/csgo/mirage_16-5_18oct2025.dem")

if not demo_path.exists():
    print(f"Demo not found: {demo_path}")
    exit(1)

print(f"Parsing: {demo_path.name}\n")

parser = DemoParser(str(demo_path))

# Parse round_end events
df = parser.parse_event("round_end")

print(f"Total rounds parsed: {len(df)}\n")
print("Round-by-round breakdown:")
print("-" * 40)

for idx, row in df.iterrows():
    print(f"Round {row['round']:2d}: {row['winner']:2s} wins - {row['reason']}")

print("-" * 40)

# Calculate final score
ct_wins = int((df['winner'] == 'CT').sum())
t_wins = int((df['winner'] == 'T').sum())

print(f"\nFinal Score:")
print(f"  CT wins: {ct_wins}")
print(f"  T wins:  {t_wins}")
print(f"  Total:   {ct_wins + t_wins}")

# Check if there are any other values in winner column
unique_winners = df['winner'].unique()
print(f"\nUnique winner values: {unique_winners}")
