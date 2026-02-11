"""Test CS2 process detection"""
import psutil

def is_cs2_running():
    """Check if CS2 is currently running."""
    for proc in psutil.process_iter(['name', 'pid']):
        if proc.info['name'].lower() in ['cs2.exe', 'cs2']:
            print(f"[OK] CS2 is running (PID: {proc.info['pid']})")
            return True
    return False

if __name__ == '__main__':
    print("=" * 60)
    print("CS2 Process Detection Test")
    print("=" * 60)

    print("\nChecking for CS2 process...")

    if is_cs2_running():
        print("\n[RESULT] CS2 is currently running")
        print("         When demo downloads, command will be copied to clipboard")
        print("         (will NOT launch a second instance)")
    else:
        print("\n[RESULT] CS2 is NOT running")
        print("         When demo downloads, CS2 will be auto-launched")

    print("\n" + "=" * 60)
    print("All running processes (for debugging):")
    print("=" * 60)

    # Show some common game processes
    game_processes = []
    for proc in psutil.process_iter(['name', 'pid']):
        name = proc.info['name'].lower()
        if any(keyword in name for keyword in ['cs', 'steam', 'game', 'epic']):
            game_processes.append(f"{proc.info['name']} (PID: {proc.info['pid']})")

    if game_processes:
        for p in game_processes[:10]:  # Show first 10
            print(f"  - {p}")
    else:
        print("  No game-related processes found")
