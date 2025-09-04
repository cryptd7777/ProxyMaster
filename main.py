import sys
try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QTabWidget, QTextEdit
    from PyQt6.QtGui import QPalette, QColor
    pyqt_version = 6
except ImportError:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QTabWidget, QTextEdit
    from PyQt5.QtGui import QPalette, QColor
    pyqt_version = 5

class ProxyMaster(QMainWindow):
    def get_proxy_history_path(self):
        import os
        return os.path.expanduser("~/.proxymaster_proxy_history.json")

    def load_proxy_history(self):
        import json, os
        path = self.get_proxy_history_path()
        if os.path.exists(path):
            with open(path, "r") as f:
                history = json.load(f)
        else:
            history = {"http_proxy": [], "https_proxy": [], "ftp_proxy": [], "no_proxy": []}
        return history

    def save_proxy_history(self, history):
        import json
        path = self.get_proxy_history_path()
        with open(path, "w") as f:
            json.dump(history, f)

    def add_to_proxy_history(self, http_proxy, https_proxy, ftp_proxy, no_proxy):
        history = self.load_proxy_history()
        def add_unique(lst, value):
            if value and value not in lst:
                lst.insert(0, value)
        add_unique(history["http_proxy"], http_proxy)
        add_unique(history["https_proxy"], https_proxy)
        add_unique(history["ftp_proxy"], ftp_proxy)
        add_unique(history["no_proxy"], no_proxy)
        self.save_proxy_history(history)
        self.update_proxy_dropdowns(history)

    def update_proxy_dropdowns(self, history=None):
        if history is None:
            history = self.load_proxy_history()
        self.http_proxy_input.clear()
        self.http_proxy_input.addItems(history["http_proxy"])
        self.https_proxy_input.clear()
        self.https_proxy_input.addItems(history["https_proxy"])
        self.ftp_proxy_input.clear()
        self.ftp_proxy_input.addItems(history["ftp_proxy"])
        self.no_proxy_input.clear()
        self.no_proxy_input.addItems(history["no_proxy"])
    def init_ui(self):
        tabs = QTabWidget()

        # Proxy tab
        proxy_tab = QWidget()
        proxy_layout = QVBoxLayout()
        self.http_proxy_input = QComboBox()
        self.http_proxy_input.setEditable(True)
        proxy_layout.addWidget(QLabel("http_proxy:"))
        proxy_layout.addWidget(self.http_proxy_input)
        self.https_proxy_input = QComboBox()
        self.https_proxy_input.setEditable(True)
        proxy_layout.addWidget(QLabel("https_proxy:"))
        proxy_layout.addWidget(self.https_proxy_input)
        self.ftp_proxy_input = QComboBox()
        self.ftp_proxy_input.setEditable(True)
        proxy_layout.addWidget(QLabel("ftp_proxy:"))
        proxy_layout.addWidget(self.ftp_proxy_input)
        self.no_proxy_input = QComboBox()
        self.no_proxy_input.setEditable(True)
        proxy_layout.addWidget(QLabel("no_proxy:"))
        proxy_layout.addWidget(self.no_proxy_input)
        self.status_label = QLabel("Proxy Status: Unknown")
        proxy_layout.addWidget(self.status_label)
        self.toggle_button = QPushButton("Toggle Proxy ON/OFF")
        self.toggle_button.clicked.connect(self.toggle_proxy)
        proxy_layout.addWidget(self.toggle_button)
        self.save_button = QPushButton("Save Proxy Settings")
        self.save_button.clicked.connect(self.save_proxy_settings)
        proxy_layout.addWidget(self.save_button)
        proxy_tab.setLayout(proxy_layout)
        tabs.addTab(proxy_tab, "Proxy")

        # Load proxy history into dropdowns at startup
        self.update_proxy_dropdowns()

        # Package manager tab
        pkg_tab = QWidget()
        pkg_layout = QVBoxLayout()
        self.pkgmanagers = self.detect_package_managers()
        self.pkgmanager_labels = {}
        self.pkgmanager_proxy_buttons = {}
        pkg_layout.addWidget(QLabel("Package Managers Detected:"))
        for pm in ["apt", "dnf", "pacman", "zypper"]:
            label = QLabel(f"{pm}: {'Found' if self.pkgmanagers.get(pm, False) else 'Not Found'}")
            pkg_layout.addWidget(label)
            self.pkgmanager_labels[pm] = label
            if self.pkgmanagers.get(pm, False):
                btn_set = QPushButton(f"Set Proxy for {pm}")
                btn_set.clicked.connect(self.make_pm_set_callback(pm))
                pkg_layout.addWidget(btn_set)
                btn_remove = QPushButton(f"Remove Proxy for {pm}")
                btn_remove.clicked.connect(self.make_pm_remove_callback(pm))
                pkg_layout.addWidget(btn_remove)
                self.pkgmanager_proxy_buttons[pm] = (btn_set, btn_remove)
        pkg_tab.setLayout(pkg_layout)
        tabs.addTab(pkg_tab, "Package Managers")

        main_layout = QVBoxLayout()
        main_layout.addWidget(tabs)

        # Log area
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #222; color: #0f0; font-family: monospace; padding: 8px;")
        main_layout.addWidget(QLabel("Command Log:"))
        main_layout.addWidget(self.log_output)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def log(self, message):
        self.log_output.append(message)
    def get_profiles_path(self):
        import os
        path = os.path.expanduser("~/.proxymaster_profiles.json")
        return path

    def load_profiles(self):
        import json, os
        path = self.get_profiles_path()
        if os.path.exists(path):
            with open(path, "r") as f:
                profiles = json.load(f)
        else:
            profiles = {"Default": {}}
        return profiles

    def save_profiles(self, profiles):
        import json
        path = self.get_profiles_path()
        with open(path, "w") as f:
            json.dump(profiles, f)

    def save_profile(self):
        profiles = self.load_profiles()
        name, ok = self.get_profile_name_dialog()
        if not ok or not name:
            return
        profiles[name] = {
            "http_proxy": self.http_proxy_input.currentText().strip(),
            "https_proxy": self.https_proxy_input.currentText().strip(),
            "ftp_proxy": self.ftp_proxy_input.currentText().strip(),
            "no_proxy": self.no_proxy_input.currentText().strip()
        }
        self.save_profiles(profiles)
        self.refresh_profiles()
        self.log(f"Profile '{name}' saved.")

    def load_profile(self, name):
        profiles = self.load_profiles()
        profile = profiles.get(name, {})
        self.http_proxy_input.setCurrentText(profile.get("http_proxy", ""))
        self.https_proxy_input.setCurrentText(profile.get("https_proxy", ""))
        self.ftp_proxy_input.setCurrentText(profile.get("ftp_proxy", ""))
        self.no_proxy_input.setCurrentText(profile.get("no_proxy", ""))
        self.log(f"Profile '{name}' loaded.")


    def refresh_profiles(self):
        profiles = self.load_profiles()
        self.profile_combo.clear()
        for name in profiles.keys():
            self.profile_combo.addItem(name)
        self.profile_combo.setCurrentText("Default")

    def get_profile_name_dialog(self):
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Save Profile", "Profile name:")
        return name, ok

    # Call refresh_profiles in __init__ after init_ui
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ProxyMaster")
        self.setGeometry(100, 100, 500, 500)
        self.init_ui()
        self.apply_theme("Light")

    # (removed duplicate old init_ui)

    def make_pm_set_callback(self, pm):
        return lambda checked=False, p=pm: self.set_package_manager_proxy(p)

    def make_pm_remove_callback(self, pm):
        return lambda checked=False, p=pm: self.remove_package_manager_proxy(p)

    def set_package_manager_proxy(self, pm):
        http_proxy = self.http_proxy_input.currentText().strip()
        https_proxy = self.https_proxy_input.currentText().strip()
        ftp_proxy = self.ftp_proxy_input.currentText().strip()
        no_proxy = self.no_proxy_input.currentText().strip()
        try:
            if pm == "apt":
                apt_conf = "/etc/apt/apt.conf.d/99proxy"
                lines = []
                if http_proxy:
                    lines.append(f'Acquire::http::Proxy "{http_proxy}";\n')
                if https_proxy:
                    lines.append(f'Acquire::https::Proxy "{https_proxy}";\n')
                if ftp_proxy:
                    lines.append(f'Acquire::ftp::Proxy "{ftp_proxy}";\n')
                with open("/tmp/apt_proxy", "w") as f:
                    f.writelines(lines)
                import subprocess
                cmd = ["pkexec", "cp", "/tmp/apt_proxy", apt_conf]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log("apt proxy set successfully.")
                else:
                    self.log(f"Error setting apt proxy: {result.stderr}")
            elif pm == "dnf":
                dnf_conf = "/etc/dnf/dnf.conf"
                import subprocess
                with open(dnf_conf, "r") as f:
                    lines = f.readlines()
                new_lines = []
                for line in lines:
                    if not line.strip().startswith("proxy="):
                        new_lines.append(line)
                if http_proxy:
                    new_lines.append(f'proxy={http_proxy}\n')
                with open("/tmp/dnf_proxy", "w") as f:
                    f.writelines(new_lines)
                cmd = ["pkexec", "cp", "/tmp/dnf_proxy", dnf_conf]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log("dnf proxy set successfully.")
                else:
                    self.log(f"Error setting dnf proxy: {result.stderr}")
            elif pm == "pacman":
                pacman_conf = "/etc/pacman.conf"
                import subprocess
                with open(pacman_conf, "r") as f:
                    lines = f.readlines()
                new_lines = []
                for line in lines:
                    if not line.strip().startswith("XferCommand = "):
                        new_lines.append(line)
                if http_proxy:
                    new_lines.append(f'XferCommand = /usr/bin/curl -x {http_proxy} -L -C - -f %u > %o\n')
                with open("/tmp/pacman_proxy", "w") as f:
                    f.writelines(new_lines)
                cmd = ["pkexec", "cp", "/tmp/pacman_proxy", pacman_conf]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log("pacman proxy set successfully.")
                else:
                    self.log(f"Error setting pacman proxy: {result.stderr}")
            elif pm == "zypper":
                zypper_conf = "/etc/zypp/zypp.conf"
                import subprocess
                with open(zypper_conf, "r") as f:
                    lines = f.readlines()
                new_lines = []
                for line in lines:
                    if not line.strip().startswith("proxy=" ):
                        new_lines.append(line)
                if http_proxy:
                    new_lines.append(f'proxy={http_proxy}\n')
                with open("/tmp/zypper_proxy", "w") as f:
                    f.writelines(new_lines)
                cmd = ["pkexec", "cp", "/tmp/zypper_proxy", zypper_conf]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log("zypper proxy set successfully.")
                else:
                    self.log(f"Error setting zypper proxy: {result.stderr}")
        except Exception as e:
            self.log(f"Error setting proxy for {pm}: {e}")

    def remove_package_manager_proxy(self, pm):
        try:
            if pm == "apt":
                import subprocess
                cmd = ["pkexec", "rm", "-f", "/etc/apt/apt.conf.d/99proxy"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log("apt proxy removed.")
                else:
                    self.log(f"Error removing apt proxy: {result.stderr}")
            elif pm == "dnf":
                dnf_conf = "/etc/dnf/dnf.conf"
                import subprocess
                with open(dnf_conf, "r") as f:
                    lines = f.readlines()
                new_lines = [line for line in lines if not line.strip().startswith("proxy=")]
                with open("/tmp/dnf_proxy", "w") as f:
                    f.writelines(new_lines)
                cmd = ["pkexec", "cp", "/tmp/dnf_proxy", dnf_conf]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log("dnf proxy removed.")
                else:
                    self.log(f"Error removing dnf proxy: {result.stderr}")
            elif pm == "pacman":
                pacman_conf = "/etc/pacman.conf"
                import subprocess
                with open(pacman_conf, "r") as f:
                    lines = f.readlines()
                new_lines = [line for line in lines if not line.strip().startswith("XferCommand = ")]
                with open("/tmp/pacman_proxy", "w") as f:
                    f.writelines(new_lines)
                cmd = ["pkexec", "cp", "/tmp/pacman_proxy", pacman_conf]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log("pacman proxy removed.")
                else:
                    self.log(f"Error removing pacman proxy: {result.stderr}")
            elif pm == "zypper":
                zypper_conf = "/etc/zypp/zypp.conf"
                import subprocess
                with open(zypper_conf, "r") as f:
                    lines = f.readlines()
                new_lines = [line for line in lines if not line.strip().startswith("proxy=")]
                with open("/tmp/zypper_proxy", "w") as f:
                    f.writelines(new_lines)
                cmd = ["pkexec", "cp", "/tmp/zypper_proxy", zypper_conf]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log("zypper proxy removed.")
                else:
                    self.log(f"Error removing zypper proxy: {result.stderr}")
        except Exception as e:
            self.log(f"Error removing proxy for {pm}: {e}")

    def detect_package_managers(self):
        import shutil
        pkgmanagers = {}
        for pm in ["apt", "dnf", "pacman", "zypper"]:
            pkgmanagers[pm] = shutil.which(pm) is not None
        return pkgmanagers

    def save_proxy_settings(self):
        import os
        import subprocess
        http_proxy = self.http_proxy_input.currentText().strip()
        https_proxy = self.https_proxy_input.currentText().strip()
        ftp_proxy = self.ftp_proxy_input.currentText().strip()
        no_proxy = self.no_proxy_input.currentText().strip()

        env_vars = {
            "http_proxy": http_proxy,
            "https_proxy": https_proxy,
            "ftp_proxy": ftp_proxy,
            "no_proxy": no_proxy
        }

        try:
            with open("/etc/environment", "r") as f:
                lines = f.readlines()
            new_lines = []
            for line in lines:
                if not any(var in line for var in env_vars.keys()):
                    new_lines.append(line)
            for var, value in env_vars.items():
                if value:
                    new_lines.append(f'{var}="{value}"\n')
            temp_env = "/tmp/proxymaster_env"
            with open(temp_env, "w") as f:
                f.writelines(new_lines)
            cmd = ["pkexec", "cp", temp_env, "/etc/environment"]
            self.log("Requesting admin password to update /etc/environment...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.log("/etc/environment updated successfully.")
                # Add to proxy history if successful
                self.add_to_proxy_history(http_proxy, https_proxy, ftp_proxy, no_proxy)
            else:
                self.log(f"Error: {result.stderr}")
            os.remove(temp_env)
        except Exception as e:
            self.log(f"Error writing to /etc/environment: {e}")

        shell = os.environ.get("SHELL", "")
        user_rc = os.path.expanduser("~/.bashrc")
        if "zsh" in shell:
            user_rc = os.path.expanduser("~/.zshrc")
        try:
            with open(user_rc, "r") as f:
                lines = f.readlines()
            new_lines = []
            for line in lines:
                if not any(var in line for var in env_vars.keys()):
                    new_lines.append(line)
            for var, value in env_vars.items():
                if value:
                    new_lines.append(f'export {var}="{value}"\n')
            with open(user_rc, "w") as f:
                f.writelines(new_lines)
            self.log("User shell config updated.")
        except Exception as e:
            self.log(f"Error writing to {user_rc}: {e}")

    def toggle_proxy(self):
        import os
        try:
            with open("/etc/environment", "r") as f:
                lines = f.readlines()
            enabled = any(line.startswith("http_proxy=") or line.startswith("https_proxy=") for line in lines)
        except Exception:
            enabled = False

        if enabled:
            try:
                new_lines = [line for line in lines if not (line.startswith("http_proxy=") or line.startswith("https_proxy=") or line.startswith("ftp_proxy=") or line.startswith("no_proxy="))]
                with open("/etc/environment", "w") as f:
                    f.writelines(new_lines)
            except Exception as e:
                print(f"Error disabling proxy in /etc/environment: {e}")

            shell = os.environ.get("SHELL", "")
            user_rc = os.path.expanduser("~/.bashrc")
            if "zsh" in shell:
                user_rc = os.path.expanduser("~/.zshrc")
            try:
                with open(user_rc, "r") as f:
                    lines = f.readlines()
                new_lines = [line for line in lines if not (line.startswith("export http_proxy=") or line.startswith("export https_proxy=") or line.startswith("export ftp_proxy=") or line.startswith("export no_proxy="))]
                with open(user_rc, "w") as f:
                    f.writelines(new_lines)
            except Exception as e:
                print(f"Error disabling proxy in {user_rc}: {e}")
            self.status_label.setText("Proxy Status: OFF")
        else:
            http_proxy = self.http_proxy_input.currentText().strip()
            https_proxy = self.https_proxy_input.currentText().strip()
            ftp_proxy = self.ftp_proxy_input.currentText().strip()
            no_proxy = self.no_proxy_input.currentText().strip()
            env_vars = {
                "http_proxy": http_proxy,
                "https_proxy": https_proxy,
                "ftp_proxy": ftp_proxy,
                "no_proxy": no_proxy
            }
            try:
                with open("/etc/environment", "r") as f:
                    lines = f.readlines()
                new_lines = [line for line in lines if not any(var in line for var in env_vars.keys())]
                for var, value in env_vars.items():
                    if value:
                        new_lines.append(f'{var}="{value}"\n')
                with open("/etc/environment", "w") as f:
                    f.writelines(new_lines)
            except Exception as e:
                print(f"Error enabling proxy in /etc/environment: {e}")

            shell = os.environ.get("SHELL", "")
            user_rc = os.path.expanduser("~/.bashrc")
            if "zsh" in shell:
                user_rc = os.path.expanduser("~/.zshrc")
            try:
                with open(user_rc, "r") as f:
                    lines = f.readlines()
                new_lines = [line for line in lines if not any(var in line for var in env_vars.keys())]
                for var, value in env_vars.items():
                    if value:
                        new_lines.append(f'export {var}="{value}"\n')
                with open(user_rc, "w") as f:
                    f.writelines(new_lines)
            except Exception as e:
                print(f"Error enabling proxy in {user_rc}: {e}")
            self.status_label.setText("Proxy Status: ON")

    def apply_theme(self, theme):
        palette = QPalette()
        if theme == "Dark":
            palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        else:
            palette = QApplication.palette()
        QApplication.instance().setPalette(palette)

if __name__ == "__main__":
    print("ProxyMaster starting...")
    app = QApplication(sys.argv)
    window = ProxyMaster()
    window.show()
    print("ProxyMaster window should be visible now.")
    sys.exit(app.exec())
