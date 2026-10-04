#!/usr/bin/env python3
"""
hypr-click-close
Zero-overhead event-driven click-to-close daemon and helper for Hyprland.
Closes application launchers (rofi, wofi, fuzzel, tofi, walker) when clicking outside.
"""

import sys
import os
import json
import time
import socket
import signal
import argparse
import subprocess

DEFAULT_LAUNCHERS = ["rofi", "wofi", "fuzzel", "tofi", "walker"]
DEFAULT_GRACE_MS = 150
BIND_KEY = ",mouse:272"

def get_hyprland_socket_path():
    xdg_runtime = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    instance = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    if not instance:
        # Fallback: look inside xdg_runtime/hypr
        hypr_dir = os.path.join(xdg_runtime, "hypr")
        if os.path.isdir(hypr_dir):
            instances = [d for d in os.listdir(hypr_dir) if os.path.exists(os.path.join(hypr_dir, d, ".socket2.sock"))]
            if instances:
                instance = sorted(instances)[-1]
    if not instance:
        raise RuntimeError("HYPRLAND_INSTANCE_SIGNATURE not found. Is Hyprland running?")
    return os.path.join(xdg_runtime, "hypr", instance, ".socket2.sock")

def hyprctl_json(cmd):
    try:
        out = subprocess.check_output(["hyprctl", cmd, "-j"], stderr=subprocess.DEVNULL)
        return json.loads(out)
    except Exception:
        return None

def hyprctl_dispatch(keyword_cmd):
    try:
        subprocess.run(["hyprctl", "keyword", *keyword_cmd], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def get_layer_surfaces(namespaces):
    layers = hyprctl_json("layers")
    if not layers:
        return []
    
    surfaces = []
    # layers can be a dict keyed by monitor name or list
    monitors_data = layers.values() if isinstance(layers, dict) else layers
    for mon_data in monitors_data:
        if not isinstance(mon_data, dict):
            continue
        levels = mon_data.get("levels", {})
        for lvl_name, layer_list in levels.items():
            for s in layer_list:
                ns = s.get("namespace", "")
                if ns in namespaces:
                    surfaces.append({
                        "namespace": ns,
                        "pid": s.get("pid"),
                        "x": float(s.get("x", 0)),
                        "y": float(s.get("y", 0)),
                        "w": float(s.get("w", s.get("width", 0))),
                        "h": float(s.get("h", s.get("height", 0))),
                    })
    return surfaces

def check_and_close(namespaces=None, grace_ms=DEFAULT_GRACE_MS, state_file=None):
    if namespaces is None:
        namespaces = DEFAULT_LAUNCHERS

    # Check grace period from state file if present
    if state_file and os.path.exists(state_file):
        try:
            with open(state_file, "r") as f:
                opened_at = float(f.read().strip())
            age_ms = (time.time() - opened_at) * 1000
            if age_ms < grace_ms:
                return
        except Exception:
            pass

    surfaces = get_layer_surfaces(namespaces)
    if not surfaces:
        # No target launcher open; unbind to stay clean
        hyprctl_dispatch(["unbind", BIND_KEY])
        return

    cursor = hyprctl_json("cursorpos")
    if not cursor:
        return
    cx, cy = float(cursor.get("x", 0)), float(cursor.get("y", 0))

    # Check if click is inside any active launcher surface
    for s in surfaces:
        rx, ry = s["x"], s["y"]
        rw, rh = s["w"], s["h"]
        if rx <= cx < rx + rw and ry <= cy < ry + rh:
            # Click is INSIDE, do not close!
            return

    # Click is OUTSIDE all surfaces -> terminate launcher(s)
    pids_to_kill = set()
    for s in surfaces:
        if s.get("pid"):
            pids_to_kill.add(s["pid"])
        else:
            # Fallback: kill by namespace
            subprocess.run(["pkill", "-x", s["namespace"]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for pid in pids_to_kill:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass

    # Immediately unbind mouse
    hyprctl_dispatch(["unbind", BIND_KEY])

def run_daemon(namespaces=None, grace_ms=DEFAULT_GRACE_MS):
    if namespaces is None:
        namespaces = DEFAULT_LAUNCHERS

    sock_path = get_hyprland_socket_path()
    self_path = os.path.abspath(__file__)
    state_file = f"/tmp/hypr-click-close-{os.getuid()}.state"

    def cleanup(*args):
        hyprctl_dispatch(["unbind", BIND_KEY])
        if os.path.exists(state_file):
            try:
                os.remove(state_file)
            except OSError:
                pass
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    print(f"[hypr-click-close] Daemon started. Monitoring namespaces: {namespaces}")

    # Reconnect loop
    while True:
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(sock_path)
            buf = ""
            active_launchers = set()

            while True:
                data = s.recv(4096).decode("utf-8", errors="ignore")
                if not data:
                    break
                buf += data
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue

                    if line.startswith("openlayer>>"):
                        ns = line.split(">>", 1)[1]
                        if ns in namespaces:
                            active_launchers.add(ns)
                            with open(state_file, "w") as f:
                                f.write(str(time.time()))
                            # Bind mouse click dynamically
                            cmd = f"{sys.executable} {self_path} --check"
                            hyprctl_dispatch(["bindn", f"{BIND_KEY},exec,{cmd}"])

                    elif line.startswith("closelayer>>"):
                        ns = line.split(">>", 1)[1]
                        active_launchers.discard(ns)
                        if not active_launchers:
                            hyprctl_dispatch(["unbind", BIND_KEY])
                            if os.path.exists(state_file):
                                try:
                                    os.remove(state_file)
                                except OSError:
                                    pass

        except Exception as e:
            time.sleep(1)

def main():
    parser = argparse.ArgumentParser(description="Zero-overhead click-to-close for Hyprland launchers")
    parser.add_argument("--check", action="store_true", help="Perform single click-position check (called by mouse bind)")
    parser.add_argument("--daemon", action="store_true", help="Run background daemon listening to Hyprland socket2")
    parser.add_argument("--grace", type=int, default=DEFAULT_GRACE_MS, help=f"Grace period in ms (default: {DEFAULT_GRACE_MS})")
    parser.add_argument("--launchers", nargs="+", default=DEFAULT_LAUNCHERS, help=f"List of launcher namespaces (default: {DEFAULT_LAUNCHERS})")
    args = parser.parse_args()

    state_file = f"/tmp/hypr-click-close-{os.getuid()}.state"

    if args.check:
        check_and_close(namespaces=args.launchers, grace_ms=args.grace, state_file=state_file)
    else:
        run_daemon(namespaces=args.launchers, grace_ms=args.grace)

if __name__ == "__main__":
    main()
