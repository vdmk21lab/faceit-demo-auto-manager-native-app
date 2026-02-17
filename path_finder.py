"""
Steam and CS2 installation path finder.
Handles multiple Steam library locations and custom installations.
"""

import os
import json
import winreg
from pathlib import Path
from typing import Optional, List
import logging


class SteamPathFinder:
    """Find Steam and CS2 installation paths on Windows."""

    # Common CS2 folder names (Valve changed the name)
    CS2_FOLDER_NAMES = [
        "Counter-Strike Global Offensive",  # Current name
        "Counter-Strike 2",                  # Possible future name
        "csgo",                              # Legacy name
    ]

    def __init__(self):
        self.steam_path: Optional[Path] = None
        self.cs2_path: Optional[Path] = None
        self.cs2_replays_path: Optional[Path] = None

    def find_steam_installation(self) -> Optional[Path]:
        """
        Find Steam installation path from Windows registry.

        Returns:
            Path to Steam installation or None if not found
        """
        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Valve\Steam"),
        ]

        for hkey, subkey in registry_paths:
            try:
                key = winreg.OpenKey(hkey, subkey)
                steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
                winreg.CloseKey(key)

                steam_path = Path(steam_path)
                if steam_path.exists():
                    logging.info(f"Found Steam installation at: {steam_path}")
                    self.steam_path = steam_path
                    return steam_path
            except (WindowsError, FileNotFoundError):
                continue

        logging.warning("Steam installation not found in registry")
        return None

    def get_steam_library_folders(self) -> List[Path]:
        """
        Get all Steam library folders from libraryfolders.vdf.

        Returns:
            List of paths to Steam library folders
        """
        if not self.steam_path:
            self.find_steam_installation()

        if not self.steam_path:
            return []

        libraries = [self.steam_path]  # Main Steam folder is always a library

        # Parse libraryfolders.vdf to find additional libraries
        vdf_path = self.steam_path / "steamapps" / "libraryfolders.vdf"

        if not vdf_path.exists():
            logging.warning(f"libraryfolders.vdf not found at {vdf_path}")
            return libraries

        try:
            with open(vdf_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple VDF parsing - look for "path" entries
            import re
            paths = re.findall(r'"path"\s+"([^"]+)"', content)

            for path_str in paths:
                # VDF uses escaped backslashes
                path_str = path_str.replace('\\\\', '\\')
                library_path = Path(path_str)

                if library_path.exists() and library_path not in libraries:
                    libraries.append(library_path)
                    logging.info(f"Found Steam library: {library_path}")

        except Exception as e:
            logging.error(f"Error parsing libraryfolders.vdf: {e}")

        return libraries

    def find_cs2_installation(self) -> Optional[Path]:
        """
        Find CS2 installation by checking all Steam library folders.

        Returns:
            Path to CS2 installation or None if not found
        """
        libraries = self.get_steam_library_folders()

        for library in libraries:
            steamapps = library / "steamapps" / "common"

            if not steamapps.exists():
                continue

            # Try different possible CS2 folder names
            for folder_name in self.CS2_FOLDER_NAMES:
                cs2_path = steamapps / folder_name

                # Check if this looks like a CS2 installation
                if cs2_path.exists():
                    # Verify it's actually CS2 by checking for key files/folders
                    game_folder = cs2_path / "game"
                    csgo_folder = game_folder / "csgo" if game_folder.exists() else cs2_path / "csgo"

                    if game_folder.exists() or csgo_folder.exists():
                        logging.info(f"Found CS2 installation at: {cs2_path}")
                        self.cs2_path = cs2_path
                        return cs2_path

        logging.warning("CS2 installation not found in any Steam library")
        return None

    def find_cs2_csgo_folder(self) -> Optional[Path]:
        """
        Find the CS2 csgo folder (where demos should be placed).

        Returns:
            Path to CS2 csgo folder or None if not found
        """
        if not self.cs2_path:
            self.find_cs2_installation()

        if not self.cs2_path:
            return None

        # Try different possible csgo folder structures
        possible_paths = [
            self.cs2_path / "game" / "csgo",
            self.cs2_path / "csgo",
        ]

        for csgo_path in possible_paths:
            if csgo_path.exists():
                logging.info(f"Found CS2 csgo folder at: {csgo_path}")
                self.cs2_replays_path = csgo_path
                return csgo_path

        logging.warning("CS2 csgo folder not found")
        return None

    def find_cs2_replays_folder(self) -> Optional[Path]:
        """
        Find the CS2 replays folder (legacy method, kept for compatibility).

        Returns:
            Path to CS2 replays folder or None if not found
        """
        # Use csgo folder instead
        return self.find_cs2_csgo_folder()

    def find_cs2_executable(self) -> Optional[Path]:
        """
        Find the CS2 executable file.

        Returns:
            Path to cs2.exe or None if not found
        """
        if not self.cs2_path:
            self.find_cs2_installation()

        if not self.cs2_path:
            return None

        # Try different possible locations
        possible_exes = [
            self.cs2_path / "game" / "bin" / "win64" / "cs2.exe",
            self.cs2_path / "cs2.exe",
        ]

        for exe_path in possible_exes:
            if exe_path.exists():
                logging.info(f"Found CS2 executable at: {exe_path}")
                return exe_path

        logging.warning("CS2 executable not found")
        return None

    def find_all_paths(self) -> dict:
        """
        Find all relevant paths and return as a dictionary.

        Returns:
            Dictionary with steam_path, cs2_path, cs2_csgo_path, and cs2_exe_path
        """
        self.find_steam_installation()
        self.find_cs2_installation()
        csgo_folder = self.find_cs2_csgo_folder()
        cs2_exe = self.find_cs2_executable()

        return {
            "steam_path": str(self.steam_path) if self.steam_path else None,
            "cs2_path": str(self.cs2_path) if self.cs2_path else None,
            "cs2_csgo_path": str(csgo_folder) if csgo_folder else None,
            "cs2_exe_path": str(cs2_exe) if cs2_exe else None,
            "steam_libraries": [str(lib) for lib in self.get_steam_library_folders()],
        }


class PathConfigManager:
    """Manage user-configured paths with fallback to auto-detection."""

    def __init__(self, config_file: str = "config.json"):
        # Use APPDATA for config file to avoid permission issues in Program Files
        import sys
        if getattr(sys, 'frozen', False):
            # Running as compiled .exe - use APPDATA
            appdata = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
            config_dir = appdata / 'FACEIT Demo Auto Manager'
            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_file = config_dir / config_file
        else:
            # Running as .py script - use same directory for development
            self.config_file = Path(__file__).parent / config_file

        self.config = self._load_config()
        self.finder = SteamPathFinder()

    def _load_config(self) -> dict:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error loading config: {e}")

        return {}

    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, indent=2, fp=f)
            logging.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logging.error(f"Error saving config: {e}")

    def get_cs2_csgo_path(self) -> Optional[Path]:
        """
        Get CS2 csgo path. Try in order:
        1. User-configured custom path
        2. Auto-detected path
        3. None if not found

        Returns:
            Path to CS2 csgo folder or None
        """
        # 1. Check user-configured path
        custom_path = self.config.get("cs2_csgo_path")
        if custom_path:
            custom_path = Path(custom_path)
            if custom_path.exists():
                logging.info(f"Using user-configured path: {custom_path}")
                return custom_path
            else:
                logging.warning(f"Configured path does not exist: {custom_path}")

        # 2. Try auto-detection
        auto_path = self.finder.find_cs2_csgo_folder()
        if auto_path:
            # Save the auto-detected path for faster access next time
            self.config["cs2_csgo_path"] = str(auto_path)
            self.save_config()
            return auto_path

        return None

    def get_cs2_replays_path(self) -> Optional[Path]:
        """Legacy method for compatibility"""
        return self.get_cs2_csgo_path()

    def set_custom_path(self, path: str) -> bool:
        """
        Set a custom CS2 replays path.

        Args:
            path: Custom path to CS2 replays folder

        Returns:
            True if path is valid and was set, False otherwise
        """
        path = Path(path)

        if not path.exists():
            logging.error(f"Custom path does not exist: {path}")
            return False

        self.config["cs2_replays_path"] = str(path)
        self.save_config()
        logging.info(f"Custom path set: {path}")
        return True

    def get_all_detected_paths(self) -> dict:
        """Get all detected paths for debugging/UI display."""
        detected = self.finder.find_all_paths()
        detected["configured_path"] = self.config.get("cs2_replays_path")
        return detected


def main():
    """Test the path finder."""
    print("=" * 60)
    print("CS2 Path Finder Test")
    print("=" * 60)

    finder = SteamPathFinder()

    print("\n1. Finding Steam installation...")
    steam_path = finder.find_steam_installation()
    if steam_path:
        print(f"   [OK] Steam found: {steam_path}")
    else:
        print("   [ERROR] Steam not found")

    print("\n2. Finding Steam library folders...")
    libraries = finder.get_steam_library_folders()
    for i, lib in enumerate(libraries, 1):
        print(f"   {i}. {lib}")

    print("\n3. Finding CS2 installation...")
    cs2_path = finder.find_cs2_installation()
    if cs2_path:
        print(f"   [OK] CS2 found: {cs2_path}")
    else:
        print("   [ERROR] CS2 not found")

    print("\n4. Finding CS2 csgo folder...")
    csgo_path = finder.find_cs2_csgo_folder()
    if csgo_path:
        print(f"   [OK] CSGO folder: {csgo_path}")
    else:
        print("   [ERROR] CSGO folder not found")

    print("\n5. Finding CS2 executable...")
    cs2_exe = finder.find_cs2_executable()
    if cs2_exe:
        print(f"   [OK] CS2 executable: {cs2_exe}")
    else:
        print("   [ERROR] CS2 executable not found")

    print("\n" + "=" * 60)
    print("Complete paths:")
    print("=" * 60)
    all_paths = finder.find_all_paths()
    print(json.dumps(all_paths, indent=2))

    print("\n" + "=" * 60)
    print("Testing PathConfigManager...")
    print("=" * 60)
    config_manager = PathConfigManager()
    csgo_path = config_manager.get_cs2_csgo_path()
    if csgo_path:
        print(f"[OK] CS2 CSGO Path: {csgo_path}")
    else:
        print("[ERROR] Could not determine CS2 csgo path")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
