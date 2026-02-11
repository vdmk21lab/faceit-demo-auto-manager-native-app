"""
Debug script to see team information and track actual team scores
"""
from pathlib import Path
from demoparser2 import DemoParser

demo_path = Path("C:/Users/VadimPrivate/Steam/steamapps/common/Counter-Strike Global Offensive/game/csgo/mirage_16-5_18oct2025.dem")

if not demo_path.exists():
    print(f"Demo not found: {demo_path}")
    exit(1)

print(f"Parsing: {demo_path.name}\n")

parser = DemoParser(str(demo_path))

# Try to get team information
print("Parsing round_end events with team data...")

# Try different team-related fields
df = parser.parse_event("round_end", other=[
    "total_rounds_played",
    "team_rounds_total_t",
    "team_rounds_total_ct"
])

print(f"\nTotal round_end events: {len(df)}")
print("\nAvailable columns:")
print(df.columns.tolist())

print("\n" + "="*80)
print("Round-by-round with team scores:")
print("="*80)

for idx, row in df.iterrows():
    round_num = row['round']
    winner = row['winner']
    reason = row['reason']
    t_score = row.get('team_rounds_total_t', 'N/A')
    ct_score = row.get('team_rounds_total_ct', 'N/A')

    print(f"Round {round_num:2d}: {winner:2s} wins ({reason:15s}) | T-side: {t_score}, CT-side: {ct_score}")

print("="*80)

# The final row should show total team scores
if len(df) > 0:
    last_row = df.iloc[-1]
    final_t = last_row.get('team_rounds_total_t', 0)
    final_ct = last_row.get('team_rounds_total_ct', 0)

    print(f"\nFinal team scores:")
    print(f"  Team on T-side start: {final_t}")
    print(f"  Team on CT-side start: {final_ct}")
    print(f"  Total rounds: {final_t + final_ct}")
