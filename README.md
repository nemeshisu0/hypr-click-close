# 🎯 hypr-click-close

[![Arch Linux](https://img.shields.io/badge/Arch%20Linux-supported-1793d1?logo=arch-linux)](https://archlinux.org)
[![Hyprland](https://img.shields.io/badge/Hyprland-Wayland-00c8ff?logo=wayland)](https://hyprland.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A **zero-overhead**, event-driven click-to-close daemon for **Hyprland**. 

Automatically closes application launchers (**Rofi**, **Wofi**, **Fuzzel**, **Tofi**, **Walker**) whenever you click outside their window — with **0.0% CPU usage** and **zero process spam** while you work or game.

---

## ⚡ The Problem with Traditional Scripts

Traditional Wayland click-to-close solutions require adding a permanent mouse binding in `hyprland.conf`:
```ini
# The old, flawed approach:
bindn = ,mouse:272,exec,click-to-close.sh
```
❌ **Why this is bad:**
1. **Constant Process Spam:** Every single left-click you make on your computer (browsing, gaming, selecting text) triggers a new subshell process executing `pgrep` and `hyprctl`.
2. **Input Latency & CPU Waste:** Rapid clicking spawns dozens of processes per second.
3. **Multi-Monitor Coordinate Bugs:** Most naive scripts compare local surface offsets against global cursor coordinates, closing the launcher even when you click *inside* on a secondary monitor.
4. **Fractional Scaling Crashes:** Floating-point coordinates from scaled displays break standard Bash integer arithmetic.

---

## 🚀 The `hypr-click-close` Solution

`hypr-click-close` connects directly to Hyprland's UNIX event socket (`socket2.sock`):

```text
[Hyprland Event Socket]
         │
         ├──► openlayer>>rofi   ──► Dynamically binds mouse:272 (only while active!)
         │
         └──► closelayer>>rofi  ──► Instantly unbinds mouse:272 (back to 0.0% overhead!)
```

### ✨ Features
- **Zero Overhead when Idle:** Absolutely no mouse interception or process execution while your launcher is closed.
- **Multi-Monitor Aware:** Accurate global coordinate translation that works across any number of monitors and multi-head setups.
- **Universal Launcher Support:** Works out-of-the-box with `rofi`, `rofi-wayland`, `wofi`, `fuzzel`, `tofi`, and `walker`.
- **Fractional Scale Proof:** Floating-point math handles 1.25x, 1.5x, and high-DPI scaling gracefully.
- **Built-in Grace Period:** Ignores clicks within the first 150ms to prevent the opening click from prematurely dismissing the menu.
- **Native Arch Linux Ready:** Includes an automated installer, `PKGBUILD`, and `systemd --user` service.

---

## 📦 Installation

### Method 1: Quick Install (Recommended)

Clone the repository and run the install script:
```bash
git clone https://github.com/your-username/hypr-click-close.git
cd hypr-click-close
./install.sh
```

This installs the binary to `~/.local/bin/hypr-click-close` and sets up the systemd service.

### Method 2: Arch Linux (`PKGBUILD`)

```bash
cd hypr-click-close
makepkg -si
```

---

## ⚙️ Configuration & Autostart

### Option A: Via Hyprland Config (Simplest)
Add this line to your `~/.config/hypr/hyprland.conf`:
```ini
exec-once = hypr-click-close --daemon
```

### Option B: Via Systemd User Service
```bash
systemctl --user daemon-reload
systemctl --user enable --now hypr-click-close.service
```

> [!NOTE]
> **Do NOT add any `bindn = ,mouse:272` to your `hyprland.conf`!** 
> The daemon dynamically injects and removes the mouse binding only when needed.

---

## 🛠️ CLI Options

```text
usage: hypr-click-close [-h] [--check] [--daemon] [--grace GRACE]
                        [--launchers LAUNCHERS [LAUNCHERS ...]]

options:
  -h, --help            Show this help message and exit
  --daemon              Run background daemon listening to Hyprland socket2 (default)
  --check               Perform single click-position check (invoked automatically by bind)
  --grace GRACE         Grace period in milliseconds to ignore initial click (default: 150)
  --launchers ...       List of layer namespaces to monitor (default: rofi wofi fuzzel tofi walker)
```

### Examples

Monitor only Rofi with a custom 200ms grace period:
```bash
hypr-click-close --daemon --launchers rofi --grace 200
```

---

## 🤝 Credits & Acknowledgements

Inspired by the original proof-of-concept by [benny-e](https://github.com/benny-e/rofi-click-to-close-hyprland). Re-architected into an event-driven daemon with multi-monitor geometry and universal launcher support.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
