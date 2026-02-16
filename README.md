# FACEIT Demo Auto Manager - Native Host

This is the native messaging host component for the FACEIT Demo Auto Manager browser extension.

## What it does

The native host processes FACEIT CS2 demo files by:
1. Decompressing `.dem.zst` files downloaded from FACEIT
2. Moving them to your CS2 csgo folder
3. Copying the `playdemo` command to clipboard for easy access

## Requirements

- Python 3.8 or higher
- Windows OS
- Counter-Strike 2 installed via Steam

## Installation

### For End Users

Download and run the installer from [releases](https://github.com/yourusername/faceit-demo-manager/releases).

The installer will:
- Install the native host executable
- Register it with Chrome/Edge
- Provide instructions for installing the browser extension

### For Developers

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy `config.example.json` to `config.json` and customize if needed (optional - auto-detection works for most users)

3. The native host will be launched automatically by the browser extension

## Building the Executable

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller --onefile --name faceit_demo_native_host native_host.py
```

The executable will be in the `dist/` folder.

## How it Works

### Native Messaging Protocol

The native host communicates with the browser extension using Chrome's Native Messaging protocol:
- Messages are exchanged via stdin/stdout
- Each message is prefixed with a 4-byte length header
- Messages are JSON-encoded

### Supported Actions

**`processDemo`** - Process a downloaded demo file
```json
{
  "action": "processDemo",
  "filePath": "C:\Users\...\demo.dem.zst"
}
```

**`getCS2Path`** - Get detected CS2 installation paths
```json
{
  "action": "getCS2Path"
}
```

**`setCS2Path`** - Set a custom CS2 path
```json
{
  "action": "setCS2Path",
  "path": "C:\Path\To\CS2\csgo"
}
```

**`deleteDemo`** - Delete a demo file from CS2 folder
```json
{
  "action": "deleteDemo",
  "demoName": "nuke_08feb2026.dem"
}
```

**`ping`** - Health check
```json
{
  "action": "ping"
}
```

## File Structure

- `native_host.py` - Main application logic and Chrome Native Messaging handler
- `path_finder.py` - Steam/CS2 installation path detection
- `com.faceit.demomanager.json` - Native messaging host manifest
- `config.example.json` - Example configuration file
- `requirements.txt` - Python dependencies

## Logging

Logs are written to `native_host.log` in the same directory as the executable/script.

This is essential for debugging since stdout is reserved for Chrome communication.

## Security

- No network connections are made
- Only processes files from FACEIT domain (verified by extension)
- Uses safe file operations (no shell execution)
- Paths are validated before use
- User-specific configurations are stored locally

## Troubleshooting

### Native host not responding

1. Check that the native host is registered:
   - Windows Registry: `HKEY_CURRENT_USER\Software\Google\Chrome\NativeMessagingHosts\com.faceit.demomanager`
   - Should point to the full path of `com.faceit.demomanager.json`

2. Check `native_host.log` for errors

3. Verify Python dependencies are installed

### CS2 path not found

The native host automatically detects CS2 installations. If auto-detection fails:

1. Use the extension popup to manually set your CS2 path
2. Or create a `config.json` file:
   ```json
   {
     "cs2_csgo_path": "C:\Path\To\CS2\game\csgo"
   }
   ```

## License

MIT License - See LICENSE file for details
