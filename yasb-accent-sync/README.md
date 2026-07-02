# YASB Accent Sync

[![GitHub](https://img.shields.io/badge/GitHub-shk0ln1k/yasb--accent--sync-blue?logo=github)](https://github.com/shk0ln1k/yasb-accent-sync)
[![PowerShell](https://img.shields.io/badge/PowerShell-5.1+-blue)](https://github.com/PowerShell/PowerShell)

> **One‑command setup for a fully adaptive Windows desktop** – Komorebi, YASB, and a Python daemon that automatically syncs your accent color from Wallpaper Engine to the entire interface.

---

## ✨ Features

- **🎨 Adaptive theming** – picks the dominant color from your current Wallpaper Engine wallpaper and applies it to:
  - YASB status bar (all widgets, backgrounds, and highlights)
  - Komorebi window borders (with rounded corners)
  - CAVA audio visualizer (gradients and foreground)
  - System‑wide accent (optional via Windows settings)
- **🚀 One‑command install** – clones the repo, installs all dependencies, copies configs, and sets up autostart
- **🔄 Live updates** – the Python daemon runs in the background and refreshes colors whenever you change your wallpaper
- **🎯 Minimal & clean** – based on the [Catppuccin‑inspired YASB theme](https://github.com/amnweb/yasb-themes/tree/main/themes/c20aec43-2e7d-4dc0-a1a8-2dc7636ca042) with system‑aware color adaptation (light/dark accent handling)
- **🖥️ No manual tweaking** – everything is pre‑configured; just install and enjoy

---

## 📦 What's Included

| Component | Description |
|-----------|-------------|
| **Komorebi** | Dynamic tiling window manager for Windows |
| **YASB** | Yet Another Status Bar – customizable top bar |
| **CAVA** | Console‑based audio visualizer (integrated into YASB) |
| **whkd** | Hotkey daemon for Komorebi (Win‑key replaced with Alt to avoid conflicts) |
| **Python daemon** | Watches Wallpaper Engine and updates CSS, YASB config, and Komorebi borders in real‑time |

---

## 🔧 Prerequisites

- **Windows 10/11** (x64)
- **PowerShell 5.1 or later** (built‑in)
- **Administrator privileges** (for installing software)
- **Internet connection** (to download installers and configs)
- **Wallpaper Engine** (Steam version recommended – for color extraction)

---

## 🚀 Quick Install

Open PowerShell **as Administrator** and run:

```powershell
git clone https://github.com/shk0ln1k/yasb-accent-sync.git
cd yasb-accent-sync
.\install.ps1
```

If you already have the required software installed and only want the configs & autostart:

```powershell
.\install.ps1 -SkipSoftwareInstall
```

The script will:
1. Install **Komorebi, whkd, YASB, CAVA**, and **Visual C++ 2012** (required for CAVA) via `winget`.
2. Start Komorebi and enable its autostart.
3. Copy all configuration files to the correct folders.
4. Install **Python 3.12** (if missing) and the `pyyaml` library.
5. Create a scheduled task to run the Python daemon at login.
6. After reboot, everything will be fully functional.

---

## 🎮 Usage After Installation

- **Change your Wallpaper Engine wallpaper** – the colors will update automatically within 5 seconds.
- **Switch accent color manually** (if you prefer): the daemon will also read the Windows accent color from the registry as a fallback.
- **Reload styles manually**: right‑click the YASB tray icon → Reload, or run `yasbc reload`.

---

## 🧩 Customization

All configs are stored in your user profile:

| File | Location | Purpose |
|------|----------|---------|
| `styles.css` | `%USERPROFILE%\.config\yasb\` | YASB styling (auto‑updated by the Python daemon) |
| `config.yaml` | `%USERPROFILE%\.config\yasb\` | YASB bar layout and widgets |
| `komorebi.json` | `%USERPROFILE%\` | Komorebi settings (tiling, borders, workspaces) |
| `whkdrc` | `%USERPROFILE%\.config\whkd\` | Komorebi hotkey definitions |
| `applications.json` | `%USERPROFILE%\` | Per‑app window rules for Komorebi |

You can tweak these files manually; the daemon will only overwrite the color variables in `styles.css` and `komorebi.json`, preserving your custom layout and settings.

---

## 🖼️ Theme Credits

This project’s visual design is heavily inspired by the **Catppuccin Macchiato** color palette and the YASB theme originally created by **amnweb**:

🔗 **[GitHub – amnweb/yasb-themes (c20aec43-2e7d-4dc0-a1a8-2dc7636ca042)](https://github.com/amnweb/yasb-themes/tree/main/themes/c20aec43-2e7d-4dc0-a1a8-2dc7636ca042)**

We adapted it to work with dynamic accent colors and added full system‑wide integration.

---

## 🐛 Troubleshooting

### “winget not found”
- Install **App Installer** from the Microsoft Store, or manually install Python, YASB, Komorebi, and CAVA, then run `install.ps1 -SkipSoftwareInstall`.

### “Python not found”
- Install Python 3.12+ from [python.org](https://python.org) (check “Add to PATH”), then re‑run the installer.

### “Cava not working”
- Make sure **Visual C++ 2012 Redistributable** is installed (the installer tries to install it automatically). If it fails, download it manually from [Microsoft](https://www.microsoft.com/en-us/download/details.aspx?id=30679).

### Colors not updating after wallpaper change
- Ensure the Python daemon is running (check Task Manager for `python.exe` with `sys_accent.py`).
- If you manually changed the system accent color, the daemon will pick it up as a fallback.

### “Reload already in progress” errors
- Wait a few seconds and try again. The YASB reload command is rate‑limited to prevent flickering.

---

## 📝 License

MIT – feel free to use, modify, and share.

---

## 🙏 Acknowledgements

- [Komorebi](https://github.com/LGUG2Z/komorebi) – by LGUG2Z
- [YASB](https://github.com/ysbaddaden/yasb) – by ysbaddaden
- [CAVA](https://github.com/karlstav/cava) – by karlstav
- [Catppuccin](https://github.com/catppuccin) – color palette inspiration
- [amnweb/yasb-themes](https://github.com/amnweb/yasb-themes) – base YASB theme (c20aec43-2e7d-4dc0-a1a8-2dc7636ca042)

---

**Enjoy your fully adaptive desktop!**  
If you encounter any issues, please open an issue on GitHub.
