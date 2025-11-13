import sys
import requests
from PySide6.QtWidgets import QApplication, QSystemTrayIcon
from PySide6.QtCore import QTimer, QThread, Signal
from PySide6.QtGui import QIcon

class StatusCheckThread(QThread):
    status_updated = Signal(bool, bool)

    def __init__(self):
        super().__init__()
        self.local_url = "http://localhost:11434"
        self.cloud_url = "https://generativelanguage.googleapis.com"

    def run(self):
        local_ok = False
        cloud_ok = False
        try:
            # Check local Ollama server. A simple HEAD request is enough.
            requests.head(self.local_url, timeout=2)
            local_ok = True
        except requests.exceptions.RequestException:
            local_ok = False

        try:
            # Check Google's API endpoint.
            requests.head(self.cloud_url, timeout=3)
            cloud_ok = True
        except requests.exceptions.RequestException:
            cloud_ok = False
            
        self.status_updated.emit(local_ok, cloud_ok)

class KaelStatusConduit:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # Icon setup
        self.icon_path = "/usr/share/icons/kael-os/"
        self.icons = {
            "ok": QIcon(self.icon_path + "kael-conduit-ok.svg"),
            "local": QIcon(self.icon_path + "kael-conduit-local.svg"),
            "cloud": QIcon(self.icon_path + "kael-conduit-cloud.svg"),
            "error": QIcon(self.icon_path + "kael-conduit-error.svg")
        }

        self.tray_icon = QSystemTrayIcon(self.icons["error"], self.app)
        self.tray_icon.setToolTip("Kael Status Conduit: Initializing...")
        self.tray_icon.show()

        # Status check logic
        self.check_thread = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_check)
        self.run_check() # Initial check
        self.timer.start(30000) # Check every 30 seconds

    def run_check(self):
        if self.check_thread is None or not self.check_thread.isRunning():
            self.check_thread = StatusCheckThread()
            self.check_thread.status_updated.connect(self.update_status)
            self.check_thread.start()

    def update_status(self, local_ok, cloud_ok):
        if local_ok and cloud_ok:
            self.tray_icon.setIcon(self.icons["ok"])
            self.tray_icon.setToolTip("Kael Animus: All Systems Online")
        elif local_ok and not cloud_ok:
            self.tray_icon.setIcon(self.icons["local"])
            self.tray_icon.setToolTip("Kael Animus: Local Core Online, Cloud Offline")
        elif not local_ok and cloud_ok:
            self.tray_icon.setIcon(self.icons["cloud"])
            self.tray_icon.setToolTip("Kael Animus: Cloud Core Online, Local Offline")
        else:
            self.tray_icon.setIcon(self.icons["error"])
            self.tray_icon.setToolTip("Kael Animus: All Systems Offline")

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    conduit = KaelStatusConduit()
    conduit.run()
