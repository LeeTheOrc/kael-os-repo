#!/usr/bin/env python
import sys
import json
import webbrowser
import requests
import google.generativeai as genai
from PySide6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QLineEdit, QVBoxLayout, QWidget, 
                               QLabel, QPushButton, QDialog, QFormLayout, QComboBox, QDialogButtonBox,
                               QHBoxLayout, QListWidget, QListWidgetItem, QMessageBox)
from PySide6.QtCore import QThread, Signal, Qt, QSettings
from PySide6.QtGui import QTextCursor, QFontDatabase, QIcon

# --- STYLESHEET ---
STYLESHEET = """
QWidget {
    font-family: Inter;
}
QMainWindow, QDialog {
    background-color: #120e1a;
    color: #ede8f9;
}
QTextEdit {
    background-color: #1a1626;
    border: 1px solid #3f345e;
    border-radius: 4px;
    color: #ede8f9;
    font-family: Monospace;
    font-size: 11pt;
}
QLineEdit {
    background-color: #221c33;
    border: 1px solid #3f345e;
    border-radius: 4px;
    padding: 8px;
    color: #ede8f9;
}
QLineEdit:focus {
    border: 1px solid #ffcc00;
}
QPushButton {
    background-color: #3f345e;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #4f446e;
}
QPushButton:pressed {
    background-color: #221c33;
}
QLabel {
    color: #a99ec3;
}
QListWidget {
    background-color: #1a1626;
    border: 1px solid #3f345e;
}
QComboBox {
    background-color: #221c33;
    border: 1px solid #3f345e;
    padding: 4px;
}
QComboBox::drop-down {
    border: none;
}
QScrollBar:vertical {
    border: none;
    background: #221c33;
    width: 8px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #3f345e;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #ffcc00;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""


# --- DIALOG FOR ADDING/EDITING API KEYS ---
class AddKeyDialog(QDialog):
    def __init__(self, parent=None, name="", key=""):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit API Key")
        self.layout = QFormLayout(self)
        self.name_input = QLineEdit(name)
        self.key_input = QLineEdit(key)
        self.key_input.setEchoMode(QLineEdit.Password)
        
        self.layout.addRow("Friendly Name:", self.name_input)
        self.layout.addRow("API Key:", self.key_input)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_data(self):
        return self.name_input.text().strip(), self.key_input.text().strip()

# --- DIALOG FOR MANAGING ALL API KEYS ---
class ManageKeysDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage API Keys")
        self.settings = QSettings("KaelOS", "KaelConsole")
        self.setMinimumWidth(500)

        self.layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)
        
        self.buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Add New Key")
        self.edit_button = QPushButton("Edit Selected")
        self.remove_button = QPushButton("Remove Selected")
        
        self.buttons_layout.addWidget(self.add_button)
        self.buttons_layout.addWidget(self.edit_button)
        self.buttons_layout.addWidget(self.remove_button)
        self.layout.addLayout(self.buttons_layout)

        self.add_button.clicked.connect(self.add_key)
        self.edit_button.clicked.connect(self.edit_key)
        self.remove_button.clicked.connect(self.remove_key)

        self.load_keys()

    def load_keys(self):
        self.list_widget.clear()
        keys_json = self.settings.value("api_keys_json", "{}")
        self.keys_dict = json.loads(keys_json)
        for name in sorted(self.keys_dict.keys()):
            self.list_widget.addItem(QListWidgetItem(name))

    def save_keys(self):
        self.settings.setValue("api_keys_json", json.dumps(self.keys_dict))
        self.parent().populate_keys_combo() # Update parent dialog

    def add_key(self):
        dialog = AddKeyDialog(self)
        
        # Create a more descriptive instructions widget
        instructions_widget = QWidget()
        instructions_layout = QVBoxLayout(instructions_widget)
        
        info_label = QLabel("Kael Console uses your personal API key to access the Cloud Animus (Gemini). For security, please generate a key and add it manually.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #a99ec3; padding-bottom: 5px;")
        
        link_label = QLabel('<a href="https://aistudio.google.com/app/apikey" style="color: #7aebbe; text-decoration: none;">1. Get your API key from Google AI Studio</a>')
        link_label.setOpenExternalLinks(True)
        
        step2_label = QLabel("2. Give it a friendly name and paste the key below.")
        step2_label.setStyleSheet("color: #a99ec3;")
        
        instructions_layout.addWidget(info_label)
        instructions_layout.addWidget(link_label)
        instructions_layout.addWidget(step2_label)
        instructions_layout.setContentsMargins(0, 0, 0, 10)

        # Add the widget to the dialog's form layout
        dialog.layout.insertRow(0, instructions_widget)
        
        if dialog.exec():
            name, key = dialog.get_data()
            if name and key:
                self.keys_dict[name] = key
                self.save_keys()
                self.load_keys()

    def edit_key(self):
        selected_item = self.list_widget.currentItem()
        if not selected_item: return
        
        name = selected_item.text()
        key = self.keys_dict.get(name, "")
        
        dialog = AddKeyDialog(self, name, key)
        if dialog.exec():
            new_name, new_key = dialog.get_data()
            if new_name and new_key:
                # Remove old key if name changed
                if name != new_name:
                    del self.keys_dict[name]
                self.keys_dict[new_name] = new_key
                self.save_keys()
                self.load_keys()

    def remove_key(self):
        selected_item = self.list_widget.currentItem()
        if not selected_item: return
        
        name = selected_item.text()
        reply = QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to remove the key '{name}'?")
        if reply == QMessageBox.Yes:
            if name in self.keys_dict:
                del self.keys_dict[name]
                self.save_keys()
                self.load_keys()

# --- MAIN SETTINGS DIALOG ---
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Guardian's Tuning Chamber")
        self.settings = QSettings("KaelOS", "KaelConsole")

        self.layout = QFormLayout(self)
        
        # AI Core Selection
        self.ai_core_combo = QComboBox()
        self.ai_core_combo.addItems(["Local Animus (Ollama)", "Cloud Animus (Gemini)"])
        self.ai_core_combo.setCurrentText(self.settings.value("ai_core", "Local Animus (Ollama)"))
        self.layout.addRow("Active AI Core:", self.ai_core_combo)

        # Local Model Profile
        self.local_model_combo = QComboBox()
        self.local_model_combo.addItems(["Inferno (llama3:8b)", "Featherlight (phi3:mini)"])
        self.local_model_combo.setCurrentText(self.settings.value("local_model_name", "Inferno (llama3:8b)"))
        self.layout.addRow("Local Animus Profile:", self.local_model_combo)

        # Gemini API Key Profile
        self.api_key_layout = QHBoxLayout()
        self.api_key_combo = QComboBox()
        self.manage_keys_button = QPushButton("Manage Keys")
        self.manage_keys_button.clicked.connect(self.open_manage_keys)
        self.api_key_layout.addWidget(self.api_key_combo)
        self.api_key_layout.addWidget(self.manage_keys_button)
        self.layout.addRow("Cloud API Key Profile:", self.api_key_layout)

        self.populate_keys_combo()
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def populate_keys_combo(self):
        self.api_key_combo.clear()
        keys_json = self.settings.value("api_keys_json", "{}")
        keys_dict = json.loads(keys_json)
        if keys_dict:
            self.api_key_combo.addItems(sorted(keys_dict.keys()))
            self.api_key_combo.setCurrentText(self.settings.value("selected_api_key_name", ""))
        else:
            self.api_key_combo.addItem("No keys configured")
            self.api_key_combo.setEnabled(False)


    def open_manage_keys(self):
        dialog = ManageKeysDialog(self)
        dialog.exec()
        # Re-enable combo if keys were added
        self.api_key_combo.setEnabled(self.api_key_combo.count() > 0 and self.api_key_combo.itemText(0) != "No keys configured")

    def accept(self):
        self.settings.setValue("ai_core", self.ai_core_combo.currentText())
        self.settings.setValue("local_model_name", self.local_model_combo.currentText())
        self.settings.setValue("selected_api_key_name", self.api_key_combo.currentText())
        super().accept()

class OllamaThread(QThread):
    response_chunk = Signal(str)
    error = Signal(str)
    finished = Signal()

    def __init__(self, prompt, model_name):
        super().__init__()
        self.prompt = prompt
        self.model_name = model_name
        self.url = "http://localhost:11434/api/generate"

    def run(self):
        payload = {"model": self.model_name, "prompt": self.prompt, "stream": True}
        try:
            with requests.post(self.url, json=payload, stream=True, timeout=10) as response:
                response.raise_for_status()
                for chunk in response.iter_lines():
                    if chunk:
                        data = json.loads(chunk)
                        self.response_chunk.emit(data.get("response", ""))
                        if data.get("done"): break
        except requests.exceptions.RequestException as e:
            self.error.emit(f"Could not connect to Kael's Local Core. Is the 'ollama' service running?\n{e}")
        finally:
            self.finished.emit()

class GeminiThread(QThread):
    response_chunk = Signal(str)
    error = Signal(str)
    finished = Signal()

    def __init__(self, prompt, api_key):
        super().__init__()
        self.prompt = prompt
        self.api_key = api_key

    def run(self):
        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(self.prompt, stream=True)
            for chunk in response:
                self.response_chunk.emit(chunk.text)
        except Exception as e:
            self.error.emit(f"Could not connect to the Cloud Animus. Is the API key correct?\n{e}")
        finally:
            self.finished.emit()

class KaelConsole(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("KaelOS", "KaelConsole")
        self.setWindowTitle("Kael Command Console")
        self.setWindowIcon(QIcon.fromTheme("kael-console"))
        self.setGeometry(100, 100, 700, 800)

        self.setStyleSheet(STYLESHEET)
        
        self.full_chat_history = "### Welcome to the Kael Command Console!\nReady for your command."
        self.worker = None

        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(11)
        
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setFont(font)
        self._update_chat_display()

        self.input_line = QLineEdit()
        self.input_line.setFont(font)
        self.input_line.setPlaceholderText("Converse with your Guardian...")
        self.input_line.returnPressed.connect(self.send_message)
        
        self.status_label = QLabel("Ready.")
        self.tuning_button = QPushButton("Tuning Chamber")
        self.tuning_button.clicked.connect(self.open_settings)

        layout = QVBoxLayout()
        layout.addWidget(self.tuning_button)
        layout.addWidget(self.chat_history)
        layout.addWidget(self.input_line)
        layout.addWidget(self.status_label)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _update_chat_display(self):
        self.chat_history.setMarkdown(self.full_chat_history)
        self.chat_history.verticalScrollBar().setValue(self.chat_history.verticalScrollBar().maximum())

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.status_label.setText("Settings saved.")

    def send_message(self):
        prompt = self.input_line.text().strip()
        if not prompt: return

        self.full_chat_history += f"\n\n**Architect:** {prompt}\n\n"
        self.input_line.clear()
        self.input_line.setEnabled(False)
        self.status_label.setText("Kael is thinking...")
        
        ai_core = self.settings.value("ai_core", "Local Animus (Ollama)")
        self.full_chat_history += f"**Kael ({ai_core.split(' ')[0]}):** "
        self._update_chat_display()

        if ai_core == "Cloud Animus (Gemini)":
            selected_key_name = self.settings.value("selected_api_key_name")
            keys_json = self.settings.value("api_keys_json", "{}")
            api_keys = json.loads(keys_json)
            api_key = api_keys.get(selected_key_name)
            
            if not api_key:
                self.append_error("No active Gemini API Key. Please select one in the Tuning Chamber.")
                return
            self.worker = GeminiThread(prompt, api_key)
        else: # Local Animus
            model_text = self.settings.value("local_model_name", "Inferno (llama3:8b)")
            model_name = "llama3:8b" if "Inferno" in model_text else "phi3:mini"
            self.worker = OllamaThread(prompt, model_name)
            
        self.worker.response_chunk.connect(self.append_response)
        self.worker.error.connect(self.append_error)
        self.worker.finished.connect(self.on_generation_finished)
        self.worker.start()

    def append_response(self, text):
        self.full_chat_history += text
        self._update_chat_display()
        
    def append_error(self, error_text):
        self.full_chat_history += f"\n\n**<font color='#ff4d4d'>Error:</font>**\n> {error_text.replace('*', '').replace('_', '')}\n\n"
        self._update_chat_display()
        self.on_generation_finished()

    def on_generation_finished(self):
        if self.worker:
            self.full_chat_history += "\n"
            self._update_chat_display()
            self.input_line.setEnabled(True)
            self.input_line.setFocus()
            self.status_label.setText("Ready.")
            self.worker = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KaelConsole()
    window.show()
    sys.exit(app.exec())
