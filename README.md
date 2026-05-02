# AOSP-CLI: Lightweight. Extensible. Iconic.

## Overview
`aosp_cli` is a high-performance productivity wrapper around the Android Debug Bridge (ADB). It abstractifies complex shell commands into a unified, registry-based interface, allowing for rapid device configuration, debugging, and profile-based automation.

## Core Architecture

### 1. The Command Registry
The tool operates on a centralized `REGISTRY` mapping. Each entry consists of:
- **Shell Template**: The raw command (supporting `{args}` injection).
- **Description**: Human-readable utility summary.
- **Tags**: Semantic categories for the search engine.

### 2. Execution Engine
The `AOSPTool.execute()` method handles command parsing. It intelligently detects if a command requires a direct `adb` call or an `adb shell` child process, ensuring seamless execution across different bridge layers.

## Installation & Usage

### Prerequisites
- Python 3.x
- `adb` (Android Debug Bridge) installed and available in `$PATH`.
- A device with **USB Debugging** enabled. (If you don't have this, what are we even doing here? We're building the future, not a lemonade stand.)

### Basic Commands
Run any command by its registry key:
```bash
./aosp_cli.py screenshot     # Capture and pull device screenshot
./aosp_cli.py dark           # Force Dark Mode system-wide
./aosp_cli.py no-anim        # Optimize speed by disabling all animations
```

### Command Search
Looking for a specific utility? The search tool queries keys, descriptions, and tags:
```bash
./aosp_cli.py search theme
```

## Advanced Automation: Profiles

Profiles allow you to batch-execute commands to reach a specific device state (e.g., "Ready for Demo" or "Debug Mode").

### Configuration (`profiles.json`)
By default, the tool looks for profiles in the same directory or at a configured path.

**Example Schema:**
```json
{
  "demo": {
    "description": "Standardize device for presentations",
    "commands": ["dark", "no-anim", "stay-awake", "clock-off"]
  }
}
```

### Running a Profile
```bash
./aosp_cli.py profile demo
```

## Full Command Reference

The registry currently supports the following commands:

| Command | Tags | Description |
| :--- | :--- | :--- |
| `anim-on` | `ui` | Enable animations |
| `bootloader` | `flashing` | Reboot to bootloader |
| `clear` | `app` | Clear app data |
| `clock-off` | `time` | Hide seconds in clock |
| `clock-on` | `time` | Show seconds in clock |
| `dark` | `theme` | Enable dark mode |
| `font-size` | `accessibility` | Set font scale |
| `force-stop` | `app` | Force stop app |
| `ip` | `network` | Show device IP |
| `key-back` | `input` | Back button |
| `key-home` | `input` | Home button |
| `layout-off` | `ui` | Hide layout bounds |
| `layout-on` | `debug` | Show layout bounds |
| `light` | `theme` | Enable light mode |
| `link` | `intent` | Open deep link |
| `log-clear` | `debug` | Clear logcat |
| `log-crash` | `debug` | Show only errors |
| `no-anim` | `speed` | Disable animations |
| `pointer-off` | `input` | Hide touch coordinates |
| `pointer-on` | `debug` | Show touch coordinates |
| `reboot` | `power` | Normal reboot |
| `record` | `video`, `record` | Record screen (CTRL+C to stop) and pull file |
| `remount` | `root` | Root and remount system |
| `screenshot` | `image`, `capture` | Capture screen, pull file, and cleanup |
| `sleep-normal` | `power` | Default sleep behavior |
| `stay-awake` | `power` | Keep screen on while charging |
| `taps-off` | `touches` | Hide touch feedback |
| `taps-on` | `touches` | Show touch feedback |
| `uninstall` | `app` | Uninstall app |

---

*“Success isn't about the code you write; it's about the friction you remove.” — Erlich Bachman (basically)*
