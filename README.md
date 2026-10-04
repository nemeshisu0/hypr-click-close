# 🎯 hypr-click-close

<div align="center">

![Hyprland Banner](https://raw.githubusercontent.com/hyprwm/Hyprland/main/assets/banner.png)

# ⚡ Zero-Overhead Click-to-Close for Hyprland Launchers
### Auto-dismiss Rofi, Wofi, Fuzzel, Tofi & Walker on external clicks with 0.0% idle CPU usage.

[![Arch Linux](https://img.shields.io/badge/Arch%20Linux-Supported-1793d1?style=for-the-badge&logo=arch-linux&logoColor=white)](https://archlinux.org)
[![Hyprland](https://img.shields.io/badge/Hyprland-Wayland%20Native-00c8ff?style=for-the-badge&logo=wayland&logoColor=white)](https://hyprland.org)
[![Python](https://img.shields.io/badge/Python-3.8+-yellow?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Systemd](https://img.shields.io/badge/Systemd-Service%20Ready-green?style=for-the-badge&logo=linux&logoColor=white)](https://systemd.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-orange?style=for-the-badge)](LICENSE)

[English](#-features) • [Italiano (Guida in Italiano)](#-guida-rapida-in-italiano) • [Installation](#-installation) • [How it Works](#-how-it-works) • [Troubleshooting](#-troubleshooting)

</div>

---

## 💡 The Problem with Traditional Scripts

On Wayland and Hyprland, application launchers like Rofi don't always grab pointer focus globally, meaning clicking outside the window leaves them stuck on screen.

Traditional workarounds force you to add a permanent mouse binding in `~/.config/hypr/hyprland.conf`:
```ini
# ❌ The old, flawed approach:
bindn = ,mouse:272,exec,click-to-close.sh
```

### Why the old approach hurts your system:
| Flaw | Old Script | 🎯 `hypr-click-close` |
| :--- | :--- | :--- |
| **Idle CPU Usage** | Spawns a new Bash subshell & `pgrep` on **every single left-click** system-wide | **0.0% CPU** (Zero background overhead) |
| **Gaming & Browsing** | Constant process spamming causing micro-stuttering during clicks | **Untouched mouse** (No binds exist when launcher is closed) |
| **Multi-Monitor** | ❌ Bugs out and closes the launcher even when clicking *inside* on a 2nd monitor | ✅ Global coordinate translation across all monitors |
| **Fractional Scaling** | ❌ Integer syntax errors on 1.25x / 1.5x scaled displays | ✅ Floating-point math handles any scale factor smoothly |
| **Launchers Supported** | Only hardcoded `rofi` | `rofi`, `rofi-wayland`, `wofi`, `fuzzel`, `tofi`, `walker` |

---

## 🧠 How It Works

Instead of intercepting every click globally, `hypr-click-close` listens directly to Hyprland's high-speed UNIX event stream (`.socket2.sock`):

```text
               ┌────────────────────────────────────────────────────────┐
               │              Hyprland UNIX Socket (.socket2)            │
               └──────────────────────────┬─────────────────────────────┘
                                          │
                   ┌──────────────────────┴──────────────────────┐
                   │                                             │
      [Event: openlayer>>rofi]                      [Event: closelayer>>rofi]
                   ▼                                             ▼
  Dynamically binds `,mouse:272`               Instantly UNBINDS `,mouse:272`
  (Only active while menu is visible!)        (Zero mouse interception when idle!)
                   │
    ┌──────────────┴──────────────┐
    ▼                             ▼
Click INSIDE menu            Click OUTSIDE menu
 └─► Keeps open (select app)   └─► Terminates launcher & cleans up
```

---

## 📦 Installation

### Method 1: Automated Installer (Recommended)

Run the included automated install script:
```bash
git clone https://github.com/nemeshisu0/hypr-click-close.git
cd hypr-click-close
chmod +x install.sh
./install.sh
```

This installs the binary to `~/.local/bin/hypr-click-close` and sets up the user systemd service.

---

### Method 2: Arch Linux (`PKGBUILD`)

If you are on Arch Linux or an Arch-based distribution:
```bash
git clone https://github.com/nemeshisu0/hypr-click-close.git
cd hypr-click-close
makepkg -si
```

---

## 🚀 Setup & Autostart

Choose **ONE** of the following options to run `hypr-click-close` in the background:

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

> [!IMPORTANT]
> **Do NOT add any permanent `bindn = ,mouse:272` in your `hyprland.conf`!**  
> The daemon dynamically injects and destroys the click listener only when an app launcher is visible on your screen.

---

## 🛠️ Configuration & CLI Options

```text
usage: hypr-click-close [-h] [--check] [--daemon] [--grace GRACE]
                        [--launchers LAUNCHERS [LAUNCHERS ...]]

Zero-overhead click-to-close daemon for Hyprland launchers

options:
  -h, --help            Show this help message and exit
  --daemon              Run background daemon listening to Hyprland socket2 (default)
  --check               Perform single click-position check (invoked by mouse bind)
  --grace GRACE         Grace period in ms to ignore click on open (default: 150)
  --launchers ...       List of layer namespaces to monitor (default: rofi wofi fuzzel tofi walker)
```

### Custom Launcher Example
If you only want to monitor `rofi` and `wofi` with a custom 200ms grace period:
```ini
exec-once = hypr-click-close --daemon --launchers rofi wofi --grace 200
```

---

## 🇮🇹 Guida Rapida in Italiano

### Che cos'è `hypr-click-close`?
È un piccolo demone a **consumo zero di CPU** per Hyprland che chiude automaticamente i menu di avvio (**Rofi**, **Wofi**, **Fuzzel**, ecc.) quando clicchi con il mouse al di fuori della loro finestra.

### Perché è migliore delle altre soluzioni?
I vecchi script richiedevano di intercettare ogni singolo click sinistro del mouse nel file `hyprland.conf`. Questo creava decine di processi inutili al secondo mentre giocavi o navigavi. `hypr-click-close` invece si sveglia solo quando il menu è aperto e lascia il mouse completamente libero per il 99.9% del tempo.

### Installazione e Avvio Rapido:
```bash
git clone https://github.com/nemeshisu0/hypr-click-close.git
cd hypr-click-close
./install.sh
```
Aggiungi questa riga nel tuo `~/.config/hypr/hyprland.conf`:
```ini
exec-once = hypr-click-close --daemon
```

---

## 🤝 Credits & Acknowledgements

* Concept inspired by the original proof-of-concept by [benny-e](https://github.com/benny-e/rofi-click-to-close-hyprland).
* Re-engineered and developed with an event-driven architecture by **nemeshisu** ([@nemeshisu0](https://github.com/nemeshisu0)).

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
