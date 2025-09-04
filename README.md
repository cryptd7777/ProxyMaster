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

### Running ProxyMaster
```bash
python3 main.py
```

### AppImage Version
You can use the AppImage version for easy distribution and running on most Linux systems. **However, you still need to install all requirements (Python, PyQt6/PyQt5, pkexec, etc.) on your system for full functionality.**

## Notes
- You may need to run with admin privileges or ensure `pkexec` is installed for system changes.
- Proxy history is stored in `~/.proxymaster_proxy_history.json`.
- The app is designed for Linux desktop environments.

## Troubleshooting
- If you see permission errors, make sure `pkexec` is installed and you have admin rights.
- If PyQt6 is not available, the app will try to use PyQt5.
- For missing package manager support, ensure the relevant manager is installed and in your PATH.

## License
MIT
