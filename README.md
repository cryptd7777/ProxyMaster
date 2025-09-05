# ProxyMaster

A Linux GUI application for managing system proxy settings and package manager proxy configuration.

## Features
- Edit and save proxy environment variables (`http_proxy`, `https_proxy`, `ftp_proxy`, `no_proxy`)
- Toggle proxy ON/OFF for system and shell
- Manage proxy settings for package managers: apt, dnf, pacman, zypper
- History of successful proxy values for quick reuse
- Dark/Light theme support
- Command log area for feedback

## Requirements
- **Python 3.7+**
- **PyQt6** (or PyQt5 as fallback)
- **pkexec** (for privilege escalation to edit `/etc/environment` and package manager configs)
- Linux system with one or more supported package managers (apt, dnf, pacman, zypper)

### Python dependencies
Install with pip:
```bash
pip install PyQt6
```
If you use PyQt5:
```bash
pip install PyQt5
```

### System dependencies
- `pkexec` (usually provided by `policykit-1`)
- Access to `/etc/environment` and package manager config files (requires admin privileges)

### Running ProxyMaster (Source Version)
```bash
python3 main.py
```

---

## AppImage Version
ðŸ‘‰ The AppImage works independently and does not require Python, PyQt, or other dependencies.  
Just **download**, **make it executable**, and **run**:

```bash
chmod +x ProxyMaster-x86_64.AppImage
./ProxyMaster-x86_64.AppImage
```

### Extra Requirements for Some Distros
Depending on your distribution, you may need to install missing libraries:

#### **openSUSE**
```bash
sudo zypper install libxcb-cursor0
```

#### **Fedora / RHEL / CentOS**
```bash
sudo dnf install libxcb libxkbcommon libxkbcommon-x11
```

#### **Ubuntu / Debian**
```bash
sudo apt install libxcb-cursor0 libxkbcommon-x11-0
```

#### **Arch / Manjaro**
```bash
sudo pacman -S libxcb libxkbcommon-x11
```

---

## Notes
- You may need to run with admin privileges or ensure `pkexec` is installed for system changes.
- Proxy history is stored in `~/.proxymaster_proxy_history.json`.
- The app is designed for Linux desktop environments.

## Troubleshooting
- If you see **permission errors**, make sure `pkexec` is installed and you have admin rights.
- If the **AppImage fails to launch**, check the section above for the required libraries on your distro.
- On Wayland desktops, some functionality may require XWayland compatibility.
