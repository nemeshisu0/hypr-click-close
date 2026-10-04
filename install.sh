#!/usr/bin/env bash
set -euo pipefail

DEST_DIR="${HOME}/.local/bin"
SYSTEMD_DIR="${HOME}/.config/systemd/user"

echo "==> Installing hypr-click-close..."

mkdir -p "${DEST_DIR}"
cp hypr_click_close.py "${DEST_DIR}/hypr-click-close"
chmod +x "${DEST_DIR}/hypr-click-close"
echo "  -> Installed executable to ${DEST_DIR}/hypr-click-close"

mkdir -p "${SYSTEMD_DIR}"
sed "s|/usr/bin/hypr-click-close|${DEST_DIR}/hypr-click-close|g" systemd/user/hypr-click-close.service > "${SYSTEMD_DIR}/hypr-click-close.service"
echo "  -> Installed systemd service to ${SYSTEMD_DIR}/hypr-click-close.service"

echo ""
echo "==> Installation complete!"
echo "You can enable and start the background daemon right now with:"
echo "    systemctl --user daemon-reload"
echo "    systemctl --user enable --now hypr-click-close.service"
echo ""
echo "Or add this line to your ~/.config/hypr/hyprland.conf:"
echo "    exec-once = hypr-click-close --daemon"
