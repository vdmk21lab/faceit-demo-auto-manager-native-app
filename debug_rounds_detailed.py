"""
Debug script to see ALL round data with more details
"""
from pathlib import Path
from demoparser2 import DemoParser

demo_path = Path("C:/Users/VadimPrivate/Steam/steamapps/common/Counter-Strike Global Offensive/game/csgo/mirage_16-5_18oct2025.dem")

if not demo_path.exists():
    print(f"Demo not found: {demo_path}")
    exit(1)

print(f"Parsing: {demo_path.name}\n")

parser = DemoParser(str(demo_path))

# Try to get game state data including round numbers and scores
print("Parsing round_end events with additional fields...")

# Parse with game state fields
df = parser.parse_event("round_end", other=["total_rounds_played", "game_phase"])

print(f"\nTotal round_end events: {len(df)}")
print("\nAll available columns:")
print(df.columns.tolist())
print("\nFirst 5 rows:")
print(df.head())
print("\nLast 5 rows:")
print(df.tail())

# Check game_phase values
if 'game_phase' in df.columns:
    print(f"\nUnique game_phase values: {df['game_phase'].unique()}")

# Try to identify warmup rounds
print("\n" + "="*60)
print("Round-by-round with game state:")
print("="*60)

for idx, row in df.iterrows():
    phase = row.get('game_phase', 'N/A')
    total_rounds = row.get('total_rounds_played', 'N/A')
    print(f"Round {row['round']:2d}: {row['winner']:2s} wins - {row['reason']:15s} | Phase: {phase} | Total: {total_rounds}")

print("="*60)

# Calculate scores
ct_wins = int((df['winner'] == 'CT').sum())
t_wins = int((df['winner'] == 'T').sum())

print(f"\nParsed Score: CT {ct_wins} - T {t_wins} (Total: {ct_wins + t_wins} rounds)")
