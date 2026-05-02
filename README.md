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

## Command Reference (Highlights)

| Command | Category | Description |
| :--- | :--- | :--- |
| `screenshot` | Capture | Captures UI and pulls to local directory |
| `layout-on` | Debug | Toggles layout bounds for UI inspection |
| `font-size` | Access | Adjusts system font scale (e.g., `font-size 1.2`) |
| `remount` | Root | Automatically handles `adb root && adb remount` |
| `link` | Intent | Triggers deep links (e.g., `link "https://example.com"`) |

---

*“Success isn't about the code you write; it's about the friction you remove.” — Erlich Bachman (basically)*
