import shutil
import sys
import time
import threading
import json
import os
import subprocess
import requests


# configurações da atualização atuomatica
CURRENT_VERSION = "2.0.0"
GITHUB_USER = "Joao-Roberto-ov"
GITHUB_REPO = "AutoClicker-and-Keyboard"
EXECUTABLE_NAME = "AutoClicker.exe"


# bootstrap: verificador de ambiente e auto-compilador

def is_running_as_exe():
    return getattr(sys, 'frozen', False)


def check_and_compile():
    if is_running_as_exe():
        return

    # Adicionei o 'requests' aqui também para garantir que o AutoUpdater funcione
    REQUIRED_MODULES = {
        'PyQt6': 'PyQt6',
        'pynput': 'pynput',
        'PyInstaller': 'pyinstaller',
        'requests': 'requests'
    }

    missing = []
    for module_import, pip_name in REQUIRED_MODULES.items():
        try:
            if module_import == 'PyInstaller':
                __import__('PyInstaller')
            else:
                __import__(module_import)
        except ImportError:
            missing.append(pip_name)

    if missing:
        missing_str = ", ".join(missing)
        print(f"\n[AVISO] As seguintes dependências estão ausentes: {missing_str}")
        answer = input("Deseja baixar e instalar automaticamente agora? (S/N): ").strip().lower()

        if answer == 's':
            try:
                for lib in missing:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
                print("Dependências instaladas com sucesso! Reiniciando o programa...")
                os.execv(sys.executable, ['python'] + sys.argv)
            except Exception as e:
                print(f"Erro ao instalar as dependências:\n{e}")
                sys.exit(1)
        else:
            sys.exit(0)

    # auto-compilador do .exe
    exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist', 'AutoClicker.exe')
    if not os.path.exists(exe_path):
        print("\n[AVISO] O executável final (.exe) ainda não foi gerado.")
        answer = input("Deseja gerar o .exe de forma automática agora? (S/N): ").strip().lower()

        if answer == 's':
            import PyInstaller.__main__
            script_path = os.path.abspath(__file__)
            PyInstaller.__main__.run([
                script_path,
                '--onefile',
                '--windowed',
                '--noconfirm',
                '--name=AutoClicker'
            ])
            print("Concluído! O executável foi gerado na pasta 'dist' ao lado deste arquivo!")


check_and_compile()


# importações do programa principal

import time
import threading
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox,
                             QGroupBox, QPushButton, QListWidget, QTextEdit,
                             QInputDialog, QMessageBox, QCheckBox, QFileDialog,
                             QLineEdit, QSplitter, QScrollArea)
from PyQt6.QtCore import pyqtSignal, QObject, QTimer, Qt
from pynput import mouse, keyboard


def key_to_str(key):
    if hasattr(key, 'name'): return f"Key.{key.name}"
    if hasattr(key, 'char') and key.char: return key.char
    return str(key)


def str_to_key(key_str):
    try:
        if key_str.startswith("Key."):
            return getattr(keyboard.Key, key_str.split(".")[1])
        return keyboard.KeyCode.from_char(key_str)
    except Exception:
        return None


def btn_to_str(btn):
    return f"Button.{btn.name}"


def str_to_btn(btn_str):
    try:
        return getattr(mouse.Button, btn_str.split(".")[1])
    except Exception:
        return mouse.Button.left


class AutoUpdater:
    @staticmethod
    def check_for_updates():
        try:
            url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                latest_version = data['tag_name'].replace('v', '')

                if latest_version > CURRENT_VERSION:
                    msg = QMessageBox()
                    msg.setWindowTitle("Atualização Obrigatória")
                    msg.setText(
                        f"Uma nova versão ({latest_version}) está disponível no servidor!\n\nVocê precisa atualizar para continuar utilizando os serviços do programa.")
                    msg.setIcon(QMessageBox.Icon.Information)

                    btn_update = msg.addButton("Atualizar Agora", QMessageBox.ButtonRole.AcceptRole)
                    msg.addButton("Sair do Programa", QMessageBox.ButtonRole.RejectRole)
                    msg.exec()

                    if msg.clickedButton() == btn_update:
                        AutoUpdater.download_and_update(data)
                    else:
                        sys.exit()
        except Exception as e:
            print(f"Erro ao checar atualizações: {e}")

    @staticmethod
    def download_and_update(release_data):
        if not getattr(sys, 'frozen', False):
            msg = QMessageBox()
            msg.warning(None, "Modo de Desenvolvimento",
                        "O programa está rodando como script .py e não pode se auto-atualizar.\n\nPara testar isso, compile o programa com o PyInstaller primeiro.")
            return

        download_url = None
        for asset in release_data.get('assets', []):
            if asset['name'] == EXECUTABLE_NAME:
                download_url = asset['browser_download_url']
                break

        if not download_url:
            msg = QMessageBox()
            msg.critical(None, "Erro Crítico", f"O arquivo {EXECUTABLE_NAME} não foi encontrado no GitHub.")
            sys.exit()

        try:
            temp_exe = "update_temp.exe"
            info = QMessageBox()
            info.setWindowTitle("Aguarde")
            info.setText("Baixando atualização... O programa será reiniciado automaticamente em instantes.")
            info.setStandardButtons(QMessageBox.StandardButton.NoButton)
            info.show()
            QApplication.processEvents()

            response = requests.get(download_url, stream=True)
            with open(temp_exe, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            current_exe = os.path.basename(sys.executable)
            bat_content = f"""@echo off\ntimeout /t 2 /nobreak > NUL\ndel "{current_exe}"\nren "{temp_exe}" "{current_exe}"\nstart "" "{current_exe}"\ndel "%~f0"\n"""
            with open("updater.bat", "w") as f:
                f.write(bat_content)

            subprocess.Popen(["updater.bat"], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            sys.exit()

        except Exception as e:
            msg = QMessageBox()
            msg.critical(None, "Erro", f"Ocorreu um erro ao tentar atualizar:\n{e}")
            sys.exit()



class WorkerSignals(QObject):
    status_update = pyqtSignal(str)
    recording_finished = pyqtSignal(list)
    event_logged = pyqtSignal(dict)
    hotkey_pressed = pyqtSignal(str)
    state_changed = pyqtSignal(str)


class MacroAutomator:
    def __init__(self, signals):
        self.events = []
        self.is_recording = False
        self.is_playing = False
        self.play_id = 0
        self.start_time = 0
        self.last_move_time = 0
        self.last_action_time = 0

        self.mouse_ctrl = mouse.Controller()
        self.keyboard_ctrl = keyboard.Controller()
        self.pressed_keys = set()
        self.pressed_buttons = set()

        self.signals = signals
        self.stop_event = threading.Event()
        self.mouse_listener = None
        self.keyboard_listener = None

    def start_recording(self):
        self.events.clear()
        self.start_time = time.time()
        self.last_move_time = self.start_time
        self.last_action_time = self.start_time
        self.signals.status_update.emit("🔴 GRAVANDO! Faça os movimentos. (Pressione F9 ou Parar)")

        self.mouse_listener = mouse.Listener(on_click=self.on_click, on_move=self.on_move)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def force_release_all(self):
        for k in list(self.pressed_keys):
            try:
                self.keyboard_ctrl.release(k)
            except:
                pass
        self.pressed_keys.clear()

        for b in list(self.pressed_buttons):
            try:
                self.mouse_ctrl.release(b)
            except:
                pass
        self.pressed_buttons.clear()

    def stop_all(self):
        self.stop_event.set()
        was_recording = self.is_recording
        self.is_recording = False
        self.is_playing = False
        self.force_release_all()

        if self.mouse_listener: self.mouse_listener.stop()
        if self.keyboard_listener: self.keyboard_listener.stop()

        if was_recording:
            self.events = [e for e in self.events if e.get('key') not in ['Key.f8', 'Key.f9', 'Key.f10']]
            self.signals.recording_finished.emit(self.events)
        else:
            self.signals.status_update.emit("Status: Parado manualmente.")

        self.signals.state_changed.emit("idle")

    def log_event(self, event_data):
        self.events.append(event_data)
        self.last_action_time = time.time()
        self.signals.event_logged.emit(event_data)

    def on_move(self, x, y):
        if self.is_recording:
            t = time.time()
            if t - self.last_move_time > 0.05:
                self.log_event({'time': t - self.start_time, 'type': 'move', 'x': x, 'y': y})
                self.last_move_time = t

    def on_click(self, x, y, button, pressed):
        if self.is_recording:
            self.log_event({'time': time.time() - self.start_time, 'type': 'click', 'x': x, 'y': y,
                            'button': btn_to_str(button), 'pressed': pressed})

    def on_press(self, key):
        if key in [keyboard.Key.f8, keyboard.Key.f9, keyboard.Key.f10]:
            if key == keyboard.Key.f9: self.stop_all()
            return
        if self.is_recording:
            self.log_event(
                {'time': time.time() - self.start_time, 'type': 'key', 'action': 'press', 'key': key_to_str(key)})

    def on_release(self, key):
        if key in [keyboard.Key.f8, keyboard.Key.f9, keyboard.Key.f10]: return
        if self.is_recording:
            self.log_event(
                {'time': time.time() - self.start_time, 'type': 'key', 'action': 'release', 'key': key_to_str(key)})

    def play(self, events, loops, interval, infinite):
        self.play_id = time.time()
        current_id = self.play_id
        self.pressed_keys.clear()
        self.pressed_buttons.clear()
        self.stop_event.clear()

        self.signals.status_update.emit("▶️ REPRODUZINDO! (Pressione F9 ou Parar)")
        loop_count = 0

        while self.is_playing and self.play_id == current_id:
            if not infinite and loop_count >= loops: break
            start_play_time = time.time()
            for event in events:
                if not self.is_playing or self.play_id != current_id: break
                target_time = start_play_time + event['time']
                delay = target_time - time.time()
                if delay > 0:
                    if self.stop_event.wait(delay): break
                if not self.is_playing or self.play_id != current_id: break

                try:
                    if event['type'] == 'move':
                        self.mouse_ctrl.position = (event['x'], event['y'])
                    elif event['type'] == 'click':
                        self.mouse_ctrl.position = (event['x'], event['y'])
                        btn = str_to_btn(event['button'])
                        if event['pressed']:
                            self.mouse_ctrl.press(btn)
                            self.pressed_buttons.add(btn)
                        else:
                            self.mouse_ctrl.release(btn)
                            self.pressed_buttons.discard(btn)
                    elif event['type'] == 'key':
                        k = str_to_key(event['key'])
                        if k:
                            if event['action'] == 'press':
                                self.keyboard_ctrl.press(k)
                                self.pressed_keys.add(k)
                            else:
                                self.keyboard_ctrl.release(k)
                                self.pressed_keys.discard(k)
                except Exception:
                    pass

            loop_count += 1
            if self.is_playing and self.play_id == current_id and (infinite or loop_count < loops):
                if self.stop_event.wait(interval): break

        if self.play_id == current_id:
            self.force_release_all()
            if self.is_playing:
                self.is_playing = False
                self.signals.status_update.emit("Status: Reprodução Concluída.")
                self.signals.state_changed.emit("idle")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Clicker & Keyboard - Perfeito 4.0")

        self.resize(850, 600)
        self.setMinimumSize(450, 350)

        self.config_file = os.path.join(os.path.expanduser("~"), ".autoclicker_config.json")
        self.current_macro_dir = ""

        self.signals = WorkerSignals()
        self.signals.status_update.connect(self.update_status)
        self.signals.recording_finished.connect(self.save_new_macro)
        self.signals.event_logged.connect(self.handle_new_event)
        self.signals.hotkey_pressed.connect(self.process_hotkey)
        self.signals.state_changed.connect(self.update_ui_state)

        self.automator = MacroAutomator(self.signals)
        self.current_events = []

        self.ui_events_log = []
        self.last_ui_event_type = None
        self.last_known_pos = (0, 0)
        self.current_move_start = (0, 0)

        self.live_timer = QTimer()
        self.live_timer.timeout.connect(self.update_live_ui)

        self.setup_ui()
        self.load_config()
        self.setup_hotkeys()

    def setup_ui(self):
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- painel esquerdo ---
        left_widget = QWidget()
        left_panel = QVBoxLayout(left_widget)
        left_widget.setMinimumWidth(250)  # Garante que a lista não será esmagada totalmente

        folder_group = QGroupBox("Gerenciamento de Pastas")
        folder_layout = QVBoxLayout()
        self.lbl_folder = QLineEdit("Nenhuma pasta selecionada")
        self.lbl_folder.setReadOnly(True)
        folder_layout.addWidget(self.lbl_folder)

        btn_select_folder = QPushButton("📁 Selecionar Pasta de Macros")
        btn_select_folder.clicked.connect(self.select_macro_folder)
        folder_layout.addWidget(btn_select_folder)

        self.btn_import = QPushButton("📥 Importar Macro Externo")
        self.btn_import.clicked.connect(self.import_macro)
        self.btn_import.setEnabled(False)
        folder_layout.addWidget(self.btn_import)

        folder_group.setLayout(folder_layout)
        left_panel.addWidget(folder_group)

        left_panel.addWidget(QLabel("📂 Macros Salvos:"))
        self.macro_list = QListWidget()
        self.macro_list.itemSelectionChanged.connect(self.display_macro_details)
        left_panel.addWidget(self.macro_list)

        btn_layout = QHBoxLayout()
        self.btn_rename = QPushButton("Renomear")
        self.btn_rename.clicked.connect(self.rename_macro)
        self.btn_delete = QPushButton("Excluir")
        self.btn_delete.clicked.connect(self.delete_macro)
        btn_layout.addWidget(self.btn_rename)
        btn_layout.addWidget(self.btn_delete)
        left_panel.addLayout(btn_layout)

        # --- painel direito ---
        right_widget = QWidget()
        right_panel = QVBoxLayout(right_widget)
        right_widget.setMinimumWidth(350)  # Garante espaço útil pros botões de play

        rec_group = QGroupBox("Controles Principais")
        rec_layout = QHBoxLayout()
        self.btn_record = QPushButton("🔴 Gravar (F8)")
        self.btn_record.clicked.connect(self.start_recording_ui)
        self.btn_play = QPushButton("▶️ Executar (F10)")
        self.btn_play.clicked.connect(self.start_playback)
        self.btn_stop = QPushButton("⏹️ Parar (F9)")
        self.btn_stop.clicked.connect(self.automator.stop_all)

        rec_layout.addWidget(self.btn_record)
        rec_layout.addWidget(self.btn_play)
        rec_layout.addWidget(self.btn_stop)
        rec_group.setLayout(rec_layout)
        right_panel.addWidget(rec_group)

        loop_group = QGroupBox("Configuração de Repetição")
        loop_layout = QHBoxLayout()

        self.check_infinite = QCheckBox("Infinito")
        loop_layout.addWidget(self.check_infinite)

        loop_layout.addWidget(QLabel("Repetições:"))
        self.loop_spin = QSpinBox()
        self.loop_spin.setRange(1, 9999)
        loop_layout.addWidget(self.loop_spin)

        loop_layout.addWidget(QLabel("Intervalo (s):"))
        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(0.0, 3600.0)
        self.interval_spin.setValue(0.5)
        loop_layout.addWidget(self.interval_spin)

        loop_group.setLayout(loop_layout)
        right_panel.addWidget(loop_group)

        right_panel.addWidget(QLabel("📝 Visualização de Comandos:"))
        self.details_box = QTextEdit()
        self.details_box.setReadOnly(True)
        self.details_box.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: Consolas;")
        right_panel.addWidget(self.details_box)

        self.status_label = QLabel("Status: Aguardando comandos...")
        self.status_label.setStyleSheet("font-weight: bold; color: #d35400;")
        right_panel.addWidget(self.status_label)

        # Adicionado os dois painéis criados ao Splitter
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)

        # Definição da proporção inicial de espaço
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 2)

        # barra de rolagem inteligente que engloba tudo
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # Faz os elementos preencherem o maximo de espaço vazio possível
        scroll_area.setWidget(main_splitter)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")  # Remove bordas de design indesejadas

        # Define a scroll area como o coração da janela
        self.setCentralWidget(scroll_area)

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    saved_dir = config.get("macro_dir", "")
                    if saved_dir and os.path.isdir(saved_dir):
                        self.set_active_directory(saved_dir)
        except Exception:
            pass

    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({"macro_dir": self.current_macro_dir}, f)
        except Exception:
            pass

    def set_active_directory(self, folder_path):
        self.current_macro_dir = folder_path
        self.lbl_folder.setText(folder_path)
        self.btn_import.setEnabled(True)
        self.load_macro_list()

    def select_macro_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta para salvar os Macros")
        if folder:
            self.set_active_directory(folder)
            self.save_config()

    def is_valid_macro(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, list): return False
            for item in data:
                if not isinstance(item, dict): return False
                if 'time' not in item or 'type' not in item: return False
                if item['type'] not in ['move', 'click', 'key']: return False
            return True
        except Exception:
            return False

    def import_macro(self):
        if not self.current_macro_dir: return
        files, _ = QFileDialog.getOpenFileNames(self, "Importar Macro(s)", "", "Arquivos JSON (*.json)")

        erros_importacao = []
        sucesso_count = 0

        for file_path in files:
            if self.is_valid_macro(file_path):
                filename = os.path.basename(file_path)
                dest = os.path.join(self.current_macro_dir, filename)
                if file_path != dest:
                    try:
                        shutil.copy(file_path, dest)
                        sucesso_count += 1
                    except Exception as e:
                        erros_importacao.append(f"{filename}: Erro ao copiar ({e})")
            else:
                erros_importacao.append(
                    f"{os.path.basename(file_path)}: Arquivo não é um macro válido ou está corrompido.")

        if erros_importacao:
            erros_str = "\n".join(erros_importacao)
            QMessageBox.critical(
                self, "Erro na Importação",
                f"Foram encontrados problemas ao importar os seguintes arquivos (eles não foram apagados do seu computador, apenas ignorados):\n\n{erros_str}"
            )

        if sucesso_count > 0:
            QMessageBox.information(self, "Sucesso", f"{sucesso_count} macro(s) importado(s) com sucesso!")
            self.load_macro_list()

    def update_ui_state(self, state):
        is_idle = (state == "idle")
        self.btn_record.setEnabled(is_idle)
        self.btn_play.setEnabled(is_idle)
        self.macro_list.setEnabled(is_idle)
        self.btn_delete.setEnabled(is_idle)
        self.btn_rename.setEnabled(is_idle)

    def setup_hotkeys(self):
        self.hotkey_listener = keyboard.GlobalHotKeys({
            '<f8>': lambda: self.signals.hotkey_pressed.emit('f8'),
            '<f9>': lambda: self.signals.hotkey_pressed.emit('f9'),
            '<f10>': lambda: self.signals.hotkey_pressed.emit('f10')
        })
        self.hotkey_listener.start()

    def process_hotkey(self, key):
        if key == 'f8':
            self.start_recording_ui()
        elif key == 'f9':
            self.automator.stop_all()
        elif key == 'f10':
            self.start_playback()

    def start_recording_ui(self):
        if not self.current_macro_dir:
            QMessageBox.warning(self, "Atenção",
                                "Você precisa selecionar uma pasta de destino antes de gravar um macro!")
            return

        if self.automator.is_recording or self.automator.is_playing: return
        self.automator.is_recording = True
        self.signals.state_changed.emit("recording")

        self.ui_events_log = ["--- Iniciando Gravação ---"]
        self.last_ui_event_type = None
        self.details_box.clear()
        self.status_label.setText("Preparando para gravar em 2 segundos...")
        QTimer.singleShot(2000, self.start_recording_actual)

    def start_recording_actual(self):
        if not self.automator.is_recording: return
        self.last_known_pos = self.automator.mouse_ctrl.position
        self.current_move_start = self.last_known_pos
        self.automator.start_recording()
        self.live_timer.start(100)

    def handle_new_event(self, e):
        if e['type'] == 'move':
            if self.last_ui_event_type == 'move':
                self.ui_events_log[-1] = f"↗️ Mouse moveu de {self.current_move_start} para ({e['x']}, {e['y']})"
            else:
                self.current_move_start = self.last_known_pos
                self.ui_events_log.append(f"↗️ Mouse moveu de {self.current_move_start} para ({e['x']}, {e['y']})")
                self.last_ui_event_type = 'move'
            self.last_known_pos = (e['x'], e['y'])
        elif e['type'] == 'click':
            btn = "Esquerdo" if "left" in e['button'] else "Direito" if "right" in e['button'] else "Meio"
            act = "Apertou" if e['pressed'] else "Soltou"
            self.ui_events_log.append(f"🖱️ {act} o botão {btn} em ({e['x']}, {e['y']})")
            self.last_ui_event_type = 'click'
            self.last_known_pos = (e['x'], e['y'])
        elif e['type'] == 'key':
            act = "Pressionou" if e['action'] == 'press' else "Soltou"
            self.ui_events_log.append(f"⌨️ {act} a tecla [{e['key']}]")
            self.last_ui_event_type = 'key'

    def update_live_ui(self):
        if self.automator.is_recording:
            idle = time.time() - self.automator.last_action_time
            text = "\n".join(self.ui_events_log)
            if idle > 0.2: text += f"\n\n⏸️ Ocioso: {idle:.1f}s..."
            self.details_box.setPlainText(text)
            sb = self.details_box.verticalScrollBar()
            sb.setValue(sb.maximum())

    def save_new_macro(self, events):
        self.live_timer.stop()
        self.details_box.setPlainText("\n".join(self.ui_events_log) + "\n\n--- Gravação Concluída ---")
        if not events:
            QMessageBox.warning(self, "Aviso", "Nenhum comando foi gravado.")
            return

        first_time = events[0]['time']
        for e in events: e['time'] -= first_time

        name, ok = QInputDialog.getText(self, "Salvar Macro", "Digite o nome para este macro:")
        if ok and name:
            filepath = os.path.join(self.current_macro_dir, f"{name}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=4)
            self.load_macro_list()
            items = self.macro_list.findItems(name, Qt.MatchFlag.MatchExactly)
            if items: self.macro_list.setCurrentItem(items[0])
            self.status_label.setText(f"Macro '{name}' salvo com sucesso!")

    def load_macro_list(self):
        self.macro_list.clear()
        if not self.current_macro_dir or not os.path.isdir(self.current_macro_dir): return
        for f in os.listdir(self.current_macro_dir):
            if f.endswith(".json"):
                self.macro_list.addItem(f.replace(".json", ""))

    def display_macro_details(self):
        if self.automator.is_recording or self.automator.is_playing: return
        items = self.macro_list.selectedItems()
        if not items: return

        name = items[0].text()
        try:
            with open(os.path.join(self.current_macro_dir, f"{name}.json"), 'r', encoding='utf-8') as f:
                events = json.load(f)
            text = f"--- Carregado: {name} ---\n(Pronto para executar)\n\n"
            text += "\n".join(self.build_log_from_events(events))
            self.details_box.setPlainText(text)
        except Exception as e:
            self.details_box.setPlainText(f"Erro: {e}")

    def build_log_from_events(self, events):
        log_lines = []
        last_type, move_start, last_pos, last_time = None, None, None, 0
        for e in events:
            delay = e['time'] - last_time
            if delay > 0.5 and last_type != 'move':
                log_lines.append(f"⏸️ Esperou {delay:.1f}s")
            if e['type'] == 'move':
                if last_type == 'move':
                    log_lines[-1] = f"↗️ Mouse moveu de {move_start} para ({e['x']}, {e['y']})"
                else:
                    move_start = last_pos if last_pos else (e['x'], e['y'])
                    log_lines.append(f"↗️ Mouse moveu de {move_start} para ({e['x']}, {e['y']})")
                    last_type = 'move'
                last_pos = (e['x'], e['y'])
            elif e['type'] == 'click':
                btn = "Esq." if "left" in e['button'] else "Dir." if "right" in e['button'] else "Meio"
                log_lines.append(f"🖱️ {'Apertou' if e['pressed'] else 'Soltou'} {btn} em ({e['x']}, {e['y']})")
                last_pos, last_type = (e['x'], e['y']), 'click'
            elif e['type'] == 'key':
                log_lines.append(f"⌨️ {'Pressionou' if e['action'] == 'press' else 'Soltou'} [{e['key']}]")
                last_type = 'key'
            last_time = e['time']
        return log_lines

    def rename_macro(self):
        items = self.macro_list.selectedItems()
        if not items: return
        old_name = items[0].text()
        new_name, ok = QInputDialog.getText(self, "Renomear", "Novo nome:", text=old_name)
        if ok and new_name:
            os.rename(os.path.join(self.current_macro_dir, f"{old_name}.json"),
                      os.path.join(self.current_macro_dir, f"{new_name}.json"))
            self.load_macro_list()

    def delete_macro(self):
        items = self.macro_list.selectedItems()
        if not items: return
        name = items[0].text()
        if QMessageBox.question(self, "Excluir", f"Excluir '{name}'?") == QMessageBox.StandardButton.Yes:
            os.remove(os.path.join(self.current_macro_dir, f"{name}.json"))
            self.details_box.clear()
            self.load_macro_list()

    def start_playback(self):
        if self.automator.is_playing or self.automator.is_recording: return
        items = self.macro_list.selectedItems()
        if not items:
            QMessageBox.warning(self, "Aviso", "Selecione um macro na lista primeiro!")
            return

        name = items[0].text()
        try:
            with open(os.path.join(self.current_macro_dir, f"{name}.json"), 'r', encoding='utf-8') as f:
                self.current_events = json.load(f)
        except Exception as e:
            QMessageBox.warning(self, "Erro crítico", f"Não foi possível ler o arquivo:\n{e}")
            return

        if not self.current_events: return
        self.automator.is_playing = True
        self.signals.state_changed.emit("playing")

        threading.Thread(target=self.automator.play,
                         args=(self.current_events, self.loop_spin.value(),
                               self.interval_spin.value(), self.check_infinite.isChecked()),
                         daemon=True).start()

    def update_status(self, text):
        self.status_label.setText(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    AutoUpdater.check_for_updates()

    window = MainWindow()
    window.show()
    sys.exit(app.exec())