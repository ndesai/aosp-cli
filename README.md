# AOSP-CLI

A lightweight, extensible command-line interface for the Android Debug Bridge (ADB). This tool abstracts complex shell commands into a unified registry, facilitating rapid device configuration, debugging, and profile-based automation.

## Features

- **Unified Command Registry**: Map complex shell sequences to simple keys.
- **Multi-Display Support**: Intelligent screenshot and screen recording across all connected displays.
- **Automotive (AAOS) Integration**: Direct support for Vehicle HAL (VHAL) property manipulation.
- **Profile Management**: Batch execution of commands for standardized environment setup.
- **Searchable Interface**: Filter and find utilities by name, description, or tag.

## Installation

### Prerequisites

- **Python 3.x**
- **Android Debug Bridge (ADB)**: Must be installed and available in `$PATH`.
- **USB Debugging**: Enabled on the target device.

### Setup

```bash
git clone https://github.com/ndesai/aosp-cli.git
cd aosp-cli
chmod +x aosp_cli.py
```

## Usage

### Basic Commands

Execute any command defined in the registry by its key:

```bash
./aosp_cli.py screenshot     # Captures all displays with activity-based naming
./aosp_cli.py dark           # Enables system-wide dark mode
./aosp_cli.py no-anim        # Disables all window and transition animations
```

### Search

Query the registry for specific utilities:

```bash
./aosp_cli.py search automotive
```

## Configuration

### Commands Registry (`commands.yaml`)

The tool uses a YAML-based registry to define commands. Each entry supports:
- `command`: The shell command to execute (supports `{args}` and `{bin_dir}`).
- `description`: A brief summary of the utility.
- `tags`: Semantic categories for indexing.

### Profiles (`profiles.json`)

Profiles allow for the sequential execution of multiple commands to establish a specific device state.

```json
{
  "demo_setup": {
    "description": "Standardize device for external presentations",
    "commands": ["dark", "no-anim", "stay-awake", "clock-off"]
  }
}
```

Run a profile using:
```bash
./aosp_cli.py profile demo_setup
```

## Full Command Reference

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
| `gear-drive` | `automotive`, `aaos`, `vhal` | Set vehicle gear to DRIVE |
| `gear-park` | `automotive`, `aaos`, `vhal` | Set vehicle gear to PARK |
| `hvac-temp` | `automotive`, `aaos`, `climate` | Set HVAC temperature for Driver |
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
| `record` | `video`, `record` | Record screen and pull file |
| `remount` | `root` | Root and remount system |
| `screenshot` | `image`, `capture`, `multi-display` | Capture all displays with activity naming |
| `sleep-normal` | `power` | Default sleep behavior |
| `stay-awake` | `power` | Keep screen on while charging |
| `taps-off` | `touches` | Hide touch feedback |
| `taps-on` | `touches` | Show touch feedback |
| `uninstall` | `app` | Uninstall app |

## Development

A pre-submit script is included to ensure the registry remains ordered:
```bash
python3 check_order.py
```
