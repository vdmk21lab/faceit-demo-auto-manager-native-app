"""
Build script for creating native_host.exe with PyInstaller

This script compiles the Python native host into a standalone .exe file
that includes Python interpreter and all dependencies.

Usage:
    python build_exe.py

Output:
    dist/faceit_demo_native_host.exe
"""

import sys
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def build_native_host():
    """Build native_host.exe with all dependencies"""

    # Check PyInstaller
    if not check_pyinstaller():
        print("ERROR: PyInstaller not found!")
        print("Please install it: pip install pyinstaller")
        sys.exit(1)

    import PyInstaller.__main__

    # Get the directory of this script
    script_dir = Path(__file__).parent

    print("=" * 60)
    print("Building FACEIT Demo Native Host")
    print("=" * 60)
    print(f"Script directory: {script_dir}")
    print(f"Main script: {script_dir / 'native_host.py'}")
    print()

    # PyInstaller arguments
    args = [
        str(script_dir / 'native_host.py'),     # Main script
        '--onefile',                             # Single .exe file
        '--noconsole',                           # No console window (runs silently)
        '--name=faceit_demo_native_host',        # Output name
        '--hidden-import=zstandard',             # Ensure zstandard is included
        '--hidden-import=psutil',                # Ensure psutil is included
        '--hidden-import=pyperclip',             # Ensure pyperclip is included
        '--hidden-import=winreg',                # Windows registry (for path detection)
        '--hidden-import=demoparser2',           # Ensure demoparser2 is included
        '--hidden-import=pandas',                # demoparser2 dependency
        '--hidden-import=polars',                # demoparser2 dependency
        '--hidden-import=pyarrow',               # demoparser2 dependency
        '--hidden-import=numpy',                 # demoparser2 dependency
        '--clean',                               # Clean PyInstaller cache
        '--noconfirm',                           # Overwrite without asking
        f'--distpath={script_dir / "dist"}',     # Output directory
        f'--workpath={script_dir / "build"}',    # Temporary build directory
        f'--specpath={script_dir}',              # .spec file location
    ]

    print("Building with PyInstaller...")
    print("This may take 1-2 minutes...")
    print()

    try:
        PyInstaller.__main__.run(args)
        print()
        print("=" * 60)
        print("✓ Build complete!")
        print("=" * 60)
        print(f"Output: {script_dir / 'dist' / 'faceit_demo_native_host.exe'}")
        print()
        print("Next steps:")
        print("1. Test the .exe: cd dist && faceit_demo_native_host.exe")
        print("2. Build the installer with Inno Setup")
        print()
    except Exception as e:
        print()
        print("=" * 60)
        print("✗ Build failed!")
        print("=" * 60)
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    build_native_host()
