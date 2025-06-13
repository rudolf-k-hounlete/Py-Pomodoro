import sys
import json
import math
import random
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# ------- ANIMATIONS DECORATIVES ---------
class AnimatedBird:
    def __init__(self, bounds):
        self.x = random.randint(0, bounds.width())
        self.y = random.randint(20, bounds.height()//2)
        self.dx = random.choice([-1, 1]) * random.uniform(1.2, 2.2)
        self.size = random.randint(20, 35)
        self.color = QColor(random.choice(["#3498DB", "#F7CA18", "#F2784B", "#16A085"]))

    def move(self, bounds):
        self.x += self.dx
        if self.x < -self.size or self.x > bounds.width()+self.size:
            self.x = -self.size if self.dx > 0 else bounds.width()+self.size
            self.y = random.randint(20, bounds.height()//2)

    def draw(self, painter):
        painter.save()
        painter.setBrush(self.color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.translate(self.x, self.y)
        painter.drawEllipse(-self.size//2, -self.size//6, self.size, self.size//2)
        painter.setBrush(QColor("#fff"))
        painter.drawEllipse(self.size//3, -self.size//12, self.size//6, self.size//6)
        painter.restore()

class AnimatedFlower:
    def __init__(self, bounds):
        self.x = random.randint(0, bounds.width())
        self.base_y = bounds.height() - 30
        self.angle = random.uniform(0, 2*math.pi)
        self.size = random.randint(18, 27)
        self.color = QColor(random.choice(["#E67E22", "#F1C40F", "#E74C3C", "#9B59B6"]))
        self.wind_phase = random.uniform(0, 2*math.pi)

    def sway(self, t):
        self.angle = math.sin(t + self.wind_phase) * 0.3

    def draw(self, painter):
        painter.save()
        painter.translate(self.x, self.base_y)
        painter.rotate(math.degrees(self.angle))
        painter.setPen(QPen(QColor("#27AE60"), 3))
        painter.drawLine(0, 0, 0, self.size)
        painter.setBrush(self.color)
        painter.setPen(Qt.PenStyle.NoPen)
        for i in range(6):
            painter.save()
            painter.rotate(i*60)
            painter.drawEllipse(int(-self.size//4), int(-self.size), self.size//2, self.size)
            painter.restore()
        painter.setBrush(QColor("#FDF6E3"))
        painter.drawEllipse(int(-self.size//5), int(-self.size//5), int(self.size//2.5), int(self.size//2.5))
        painter.restore()

# ------- TIMER LOGIC ---------
class PomodoroTimer(QTimer):
    timeChanged = pyqtSignal(int)
    sessionCompleted = pyqtSignal(str)
    paused = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()
        self.timeout.connect(self.updateTime)
        self.remaining_time = 0
        self.session_type = "work"
        self.paused_flag = False

    def startSession(self, duration, session_type):
        self.remaining_time = duration
        self.session_type = session_type
        self.paused_flag = False
        self.start(1000)

    def updateTime(self):
        if self.paused_flag:
            return
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.timeChanged.emit(self.remaining_time)
        else:
            self.stop()
            self.sessionCompleted.emit(self.session_type)

    def pause(self):
        self.paused_flag = True

    def resume(self):
        self.paused_flag = False

    def reset(self):
        self.stop()
        self.paused_flag = False

# ------- CIRCULAR PROGRESS WITH ANIMATION & DECOR ---------
class CircularProgressWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(340, 340)
        self.progress = 0
        self.total_time = 1500
        self.remaining_time = 1500
        self.session_type = "work"
        self.theme_colors = {
            "modern": {"work": "#FF6B6B", "break": "#4ECDC4", "long_break": "#45B7D1"},
            "forest": {"work": "#2ECC71", "break": "#27AE60", "long_break": "#16A085"},
            "sunset": {"work": "#E67E22", "break": "#F39C12", "long_break": "#D35400"},
            "ocean": {"work": "#3498DB", "break": "#5DADE2", "long_break": "#2980B9"},
            "dark": {"work": "#8E44AD", "break": "#9B59B6", "long_break": "#7D3C98"},
            "zen": {"work": "#B7E9F7", "break": "#FFEDC2", "long_break": "#FDC2D1"}
        }
        self.current_theme = "modern"
        self._animation_progress = 0
        self._anim_timer = QTimer()
        self._anim_timer.timeout.connect(self._animate)
        self._anim_timer.start(50)
        self.birds = [AnimatedBird(self.rect()) for _ in range(3)]
        self.flowers = [AnimatedFlower(self.rect()) for _ in range(4)]
        self._time_anim = 0

    def setProgress(self, remaining, total, session_type):
        self.remaining_time = remaining
        self.total_time = total
        self.session_type = session_type
        desired_progress = (total - remaining) / total
        if abs(self.progress - desired_progress) > 0.01:
            self._target_progress = desired_progress
        else:
            self.progress = desired_progress
        self.update()

    def setTheme(self, theme):
        if theme in self.theme_colors:
            self.current_theme = theme
        self.update()

    def _animate(self):
        if hasattr(self, '_target_progress'):
            diff = self._target_progress - self.progress
            self.progress += diff * 0.1
            if abs(diff) < 0.01:
                self.progress = self._target_progress
                del self._target_progress
            self.update()
        for bird in self.birds:
            bird.move(self.rect())
        self._time_anim += 0.06
        for flower in self.flowers:
            flower.sway(self._time_anim)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QRadialGradient(self.width()//2, self.height()//2, self.width()//2)
        gradient.setColorAt(0, QColor("#f8fafc"))
        gradient.setColorAt(1, QColor("#e9ecef"))
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, self.width(), self.height())
        for flower in self.flowers:
            flower.draw(painter)
        color = QColor(self.theme_colors[self.current_theme][self.session_type])
        remaining_percent = self.remaining_time / self.total_time if self.total_time else 1
        if remaining_percent < 0.1:
            color = QColor("#FF4757")
        elif remaining_percent < 0.25:
            color = QColor("#FFA502")
        painter.setPen(QPen(color, 12, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        start_angle = 90 * 16
        span_angle = -int(self.progress * 360 * 16)
        painter.drawArc(25, 25, 290, 290, start_angle, span_angle)
        painter.setPen(QColor("#212121"))
        font = QFont("Segoe UI", 38, QFont.Weight.Bold)
        painter.setFont(font)
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        time_text = f"{minutes:02d}:{seconds:02d}"
        painter.drawText(QRect(0, 65, 340, 90), Qt.AlignmentFlag.AlignCenter, time_text)
        painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        painter.setPen(QColor(100, 100, 100))
        session_names = {"work": "TRAVAIL", "break": "PAUSE", "long_break": "PAUSE LONGUE"}
        painter.drawText(QRect(0, 170, 340, 40), Qt.AlignmentFlag.AlignCenter, session_names.get(self.session_type, "SESSION"))
        for bird in self.birds:
            bird.draw(painter)
        painter.end()

# --------- BUTTONS ---------
class IconButton(QPushButton):
    def __init__(self, icon, tooltip="", color="#4ECDC4"):
        super().__init__()
        self.setIcon(icon)
        self.setIconSize(QSize(32, 32))
        self.setToolTip(tooltip)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;
                border-radius: 18px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: #2C3E50;
            }}
        """)

class ModernButton(QPushButton):
    def __init__(self, text, color="#4ECDC4", icon=None):
        super().__init__(text)
        self.color = color
        self.setFixedHeight(48)
        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(24, 24))
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;
                color: white;
                font-size: 17px;
                font-family: 'Segoe UI';
                font-weight: 600;
                border-radius: 24px;
                padding: 12px 28px;
                letter-spacing: 1.2px;
            }}
            QPushButton:hover {{
                background-color: {self.adjustColor(color, 0.85)};
                transform: scale(1.04);
            }}
            QPushButton:pressed {{
                background-color: {self.adjustColor(color, 0.7)};
            }}
        """)

    def adjustColor(self, color, factor):
        c = QColor(color)
        r = min(255, int(c.red() * factor))
        g = min(255, int(c.green() * factor))
        b = min(255, int(c.blue() * factor))
        return f"rgb({r},{g},{b})"

# --------- HISTORY ---------
class SessionHistoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self._all_sessions = []

    def initUI(self):
        layout = QVBoxLayout(self)
        title_bar = QHBoxLayout()
        title = QLabel("Historique des séances")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #455A64; margin-bottom: 15px;")
        title_bar.addWidget(title)
        title_bar.addStretch()
        export_btn = IconButton(QIcon("document-save"), "Exporter l'historique", "#FDCB6E")
        title_bar.addWidget(export_btn)
        import_btn = IconButton(QIcon("document-open"), "Importer", "#B2BEC3")
        title_bar.addWidget(import_btn)
        layout.addLayout(title_bar)
        self.history_list = QListWidget()
        self.history_list.setAlternatingRowColors(True)
        self.history_list.setStyleSheet("""
            QListWidget {
                border: none;
                background: #F9FAFB;
                font-size: 15px;
                border-radius: 16px;
            }
            QListWidget::item:selected {
                background: #D6EAF8;
            }
        """)
        layout.addWidget(self.history_list, stretch=1)
        stats_bar = QHBoxLayout()
        self.total_sessions = QLabel("Total: 0")
        self.total_time = QLabel("Total temps: 0h 0m")
        self.avg_session = QLabel("Moyenne: 0m")
        self.streak_label = QLabel("Streak: 0j")
        for l in [self.total_sessions, self.total_time, self.avg_session, self.streak_label]:
            l.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            l.setStyleSheet("color: #636E72;")
            stats_bar.addWidget(l)
        stats_bar.addStretch()
        layout.addLayout(stats_bar)

    def addSession(self, session_type, duration, completed_time):
        self._all_sessions.append((session_type, duration, completed_time))
        session_names = {"work": "Travail", "break": "Pause", "long_break": "Pause longue"}
        icon = QIcon("clock") if session_type == "work" else QIcon("media-playback-pause")
        duration_min = duration // 60
        text = f"{session_names.get(session_type, 'Session')} • {duration_min}m • {completed_time.strftime('%H:%M %d/%m/%Y')}"
        item = QListWidgetItem(icon, text)
        self.history_list.insertItem(0, item)
        self.updateStats()

    def updateStats(self):
        count = sum(1 for s in self._all_sessions if s[0]=="work")
        self.total_sessions.setText(f"Total: {count}")
        total_minutes = sum(d//60 for (tp, d, _) in self._all_sessions if tp=="work")
        hours = total_minutes // 60
        minutes = total_minutes % 60
        self.total_time.setText(f"Total temps: {hours}h {minutes}m")
        self.avg_session.setText(f"Moyenne: {total_minutes//count if count else 0}m")

# --------- PARAMÈTRES ---------
class SettingsWidget(QWidget):
    settingsChanged = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.settings = {
            "work_duration": 25,
            "break_duration": 5,
            "long_break_duration": 15,
            "sessions_until_long_break": 4,
            "auto_start_breaks": False,
            "auto_start_work": False,
            "theme": "modern",
            "notifications": True,
            "sound_enabled": True,
            "mode_zen": False
        }
        self.initUI()

    def initUI(self):
        self.setStyleSheet("""QScrollArea{ background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F8F9FA, stop:1 #E9ECEF); }
                            QWidget{ background: transparent; }
                            QLayout{ background: transparent; }
                            QVBoxLayout{ background: transparent; }
                           """)
        layout = QVBoxLayout(self)
        title = QLabel("Paramètres")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2C3E50; margin-bottom: 20px;")
        layout.addWidget(title)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none; background: transparent;}")
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        time_group = self.createGroup("Durées (minutes)")
        time_layout = QFormLayout()
        self.work_spin = QSpinBox()
        self.work_spin.setRange(1, 120)
        self.work_spin.setValue(self.settings["work_duration"])
        self.work_spin.valueChanged.connect(self.updateSettings)
        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 60)
        self.break_spin.setValue(self.settings["break_duration"])
        self.break_spin.valueChanged.connect(self.updateSettings)
        self.long_break_spin = QSpinBox()
        self.long_break_spin.setRange(1, 120)
        self.long_break_spin.setValue(self.settings["long_break_duration"])
        self.long_break_spin.valueChanged.connect(self.updateSettings)
        self.sessions_spin = QSpinBox()
        self.sessions_spin.setRange(2, 10)
        self.sessions_spin.setValue(self.settings["sessions_until_long_break"])
        self.sessions_spin.valueChanged.connect(self.updateSettings)
        time_layout.addRow("Travail:", self.work_spin)
        time_layout.addRow("Pause courte:", self.break_spin)
        time_layout.addRow("Pause longue:", self.long_break_spin)
        time_layout.addRow("Séances avant pause longue:", self.sessions_spin)
        time_group.setLayout(time_layout)
        settings_layout.addWidget(time_group)
        behavior_group = self.createGroup("Comportement")
        behavior_layout = QVBoxLayout()
        self.auto_start_breaks_cb = QCheckBox("Démarrer automatiquement les pauses")
        self.auto_start_breaks_cb.setChecked(self.settings["auto_start_breaks"])
        self.auto_start_breaks_cb.toggled.connect(self.updateSettings)
        self.auto_start_work_cb = QCheckBox("Démarrer automatiquement le travail")
        self.auto_start_work_cb.setChecked(self.settings["auto_start_work"])
        self.auto_start_work_cb.toggled.connect(self.updateSettings)
        self.notifications_cb = QCheckBox("Notifications")
        self.notifications_cb.setChecked(self.settings["notifications"])
        self.notifications_cb.toggled.connect(self.updateSettings)
        self.sound_cb = QCheckBox("Sons")
        self.sound_cb.setChecked(self.settings["sound_enabled"])
        self.sound_cb.toggled.connect(self.updateSettings)
        self.zen_cb = QCheckBox("Mode Zen (désactive les sons, animations, couleurs douces)")
        self.zen_cb.setChecked(self.settings.get("mode_zen", False))
        self.zen_cb.toggled.connect(self.updateSettings)
        for cb in [self.auto_start_breaks_cb, self.auto_start_work_cb, self.notifications_cb, self.sound_cb, self.zen_cb]:
            behavior_layout.addWidget(cb)
        behavior_group.setLayout(behavior_layout)
        settings_layout.addWidget(behavior_group)
        theme_group = self.createGroup("Thème")
        theme_layout = QVBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["modern", "forest", "sunset", "ocean", "dark", "zen"])
        self.theme_combo.setCurrentText(self.settings["theme"])
        self.theme_combo.currentTextChanged.connect(self.updateSettings)
        theme_layout.addWidget(QLabel("Sélectionner un thème:"))
        theme_layout.addWidget(self.theme_combo)
        theme_group.setLayout(theme_layout)
        settings_layout.addWidget(theme_group)
        settings_layout.addStretch()
        scroll.setWidget(settings_widget)
        layout.addWidget(scroll)

    def createGroup(self, title):
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold; color: #2C3E50; border: 2px solid #CCC; border-radius: 12px; margin-top: 12px; padding-top: 12px; 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F8F9FA, stop:1 #E9ECEF);
            }
            QGroupBox::title { left: 10px; color: #2C3E50;}
            QLabel { color: #2C3E50; }
            QCheckBox { color: #2C3E50; font-size: 14px; }
            QSpinBox, QLineEdit { background: #fff; border: 1px solid #CCC; border-radius: 8px; padding: 6px; font-size: 14px; color: #2C3E50; }
            QComboBox { background: #fff; border: 1px solid #CCC; border-radius: 8px; padding: 6px; font-size: 14px; color: #2C3E50; }
        """)
        return group

    def updateSettings(self):
        self.settings.update({
            "work_duration": self.work_spin.value(),
            "break_duration": self.break_spin.value(),
            "long_break_duration": self.long_break_spin.value(),
            "sessions_until_long_break": self.sessions_spin.value(),
            "auto_start_breaks": self.auto_start_breaks_cb.isChecked(),
            "auto_start_work": self.auto_start_work_cb.isChecked(),
            "theme": self.theme_combo.currentText(),
            "notifications": self.notifications_cb.isChecked(),
            "sound_enabled": self.sound_cb.isChecked(),
            "mode_zen": self.zen_cb.isChecked()
        })
        self.settingsChanged.emit(self.settings)

# --------- MAIN APP ---------
class PomodoroApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.timer = PomodoroTimer()
        self.timer.timeChanged.connect(self.updateDisplay)
        self.timer.sessionCompleted.connect(self.onSessionCompleted)
        self.current_session = "work"
        self.session_count = 0
        self.is_running = False
        self.initUI()
        self.loadSettings()
        self.setWindowTitle("🍅 Pomodoro Pro Ultra")

    def initUI(self):
        self.setFixedSize(900, 680)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        nav_bar = self.createNavigationBar()
        main_layout.addWidget(nav_bar)
        self.stacked_widget = QStackedWidget()
        self.timer_widget = self.createTimerWidget()
        self.stacked_widget.addWidget(self.timer_widget)
        self.settings_widget = SettingsWidget()
        self.settings_widget.settingsChanged.connect(self.applySettings)
        self.stacked_widget.addWidget(self.settings_widget)
        self.history_widget = SessionHistoryWidget()
        self.stacked_widget.addWidget(self.history_widget)
        main_layout.addWidget(self.stacked_widget)
        self.setStyleSheet("""
            QMainWindow { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F8F9FA, stop:1 #E9ECEF);
            }
        """)

    def createNavigationBar(self):
        nav_widget = QWidget()
        nav_widget.setFixedHeight(62)
        nav_widget.setStyleSheet("""
            QWidget { 
                background: #fff; 
                border-bottom: 1.5px solid #E9ECEF;
            }
        """)
        layout = QHBoxLayout(nav_widget)
        layout.setContentsMargins(22, 0, 22, 0)
        title = QLabel("🍅 Pomodoro Pro Ultra")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2C3E50; letter-spacing:1.8px;")
        layout.addWidget(title)
        layout.addStretch()
        self.nav_buttons = {}
        timer_btn = QPushButton("Timer")
        timer_btn.clicked.connect(lambda: self.switchView(0))
        self.nav_buttons["timer"] = timer_btn
        history_btn = QPushButton("Historique")
        history_btn.clicked.connect(lambda: self.switchView(2))
        self.nav_buttons["history"] = history_btn
        settings_btn = QPushButton("Paramètres")
        settings_btn.clicked.connect(lambda: self.switchView(1))
        self.nav_buttons["settings"] = settings_btn
        menu_btn = QPushButton("Menu")
        menu_btn.clicked.connect(self.showMenuPopup)
        self.nav_buttons["menu"] = menu_btn
        for btn in [timer_btn, history_btn, settings_btn, menu_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent; 
                    border: none; 
                    color: #7F8C8D; 
                    font-size: 15px; 
                    font-weight: bold;
                    padding: 12px 18px; 
                    border-radius: 10px;
                }
                QPushButton:hover { 
                    background: #F1F2F6; 
                    color: #2C3E50;
                }
                QPushButton:checked { 
                    background: #4ECDC4; 
                    color: white;
                }
            """)
            btn.setCheckable(True)
            layout.addWidget(btn)
        timer_btn.setChecked(True)
        return nav_widget

    def createTimerWidget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(28)
        self.progress_widget = CircularProgressWidget()
        layout.addWidget(self.progress_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(18)
        self.start_pause_btn = ModernButton("Démarrer", "#4ECDC4")
        self.start_pause_btn.clicked.connect(self.toggleTimer)
        self.start_pause_btn.setFixedWidth(150)
        self.reset_btn = ModernButton("Reset", "#FF6B6B")
        self.reset_btn.clicked.connect(self.resetTimer)
        self.reset_btn.setFixedWidth(120)
        self.skip_btn = ModernButton("Passer", "#95A5A6")
        self.skip_btn.clicked.connect(self.skipSession)
        self.skip_btn.setFixedWidth(120)
        controls_layout.addWidget(self.start_pause_btn)
        controls_layout.addWidget(self.reset_btn)
        controls_layout.addWidget(self.skip_btn)
        layout.addLayout(controls_layout)
        self.session_info = QLabel("Prêt à commencer")
        self.session_info.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        self.session_info.setStyleSheet("color: #7F8C8D; margin-top: 10px; letter-spacing:1.2px;")
        self.session_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.session_info)
        self.focus_label = QLabel("")
        self.focus_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.focus_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.focus_label.setStyleSheet("color:#95A5A6;")
        layout.addWidget(self.focus_label)
        return widget

    def switchView(self, idx):
        self.stacked_widget.setCurrentIndex(idx)
        for k, btn in self.nav_buttons.items():
            btn.setChecked(False)
        if idx == 0: self.nav_buttons["timer"].setChecked(True)
        elif idx == 1: self.nav_buttons["settings"].setChecked(True)
        elif idx == 2: self.nav_buttons["history"].setChecked(True)

    def showMenuPopup(self):
        menu = QMenu()
        act1 = QAction("À propos", self)
        act1.triggered.connect(lambda: self.setInfoMode("Pomodoro Pro Ultra\nModern, créatif & open source."))
        act2 = QAction("Mode Focus", self)
        act2.triggered.connect(self.toggleFocusMode)
        act3 = QAction("Mode Zen", self)
        act3.triggered.connect(self.toggleZenMode)
        act4 = QAction("Quitter", self)
        act4.triggered.connect(self.close)
        menu.addAction(act1)
        menu.addAction(act2)
        menu.addAction(act3)
        menu.addSeparator()
        menu.addAction(act4)
        menu.exec(self.mapToGlobal(self.nav_buttons["menu"].pos() + QPoint(60, 50)))

    def setInfoMode(self, msg):
        self.focus_label.setText(msg)
        QTimer.singleShot(4000, lambda: self.focus_label.setText(""))

    def toggleFocusMode(self):
        if self.focus_label.text() == "MODE FOCUS ACTIVÉ":
            self.focus_label.setText("")
        else:
            self.focus_label.setText("MODE FOCUS ACTIVÉ")
        QTimer.singleShot(7000, lambda: self.focus_label.setText(""))

    def toggleZenMode(self):
        s = self.settings_widget.settings
        s["mode_zen"] = not s["mode_zen"]
        self.settings_widget.zen_cb.setChecked(s["mode_zen"])
        self.applySettings(s)

    def toggleTimer(self):
        if not self.is_running:
            self.startCurrentSession()
        else:
            self.pauseTimer()

    def startCurrentSession(self):
        duration = self.getSessionDuration(self.current_session)
        self.timer.startSession(duration * 60, self.current_session)
        self.is_running = True
        self.start_pause_btn.setText("Pause")
        self.updateSessionInfo()

    def pauseTimer(self):
        self.timer.pause()
        self.is_running = False
        self.start_pause_btn.setText("Reprendre")

    def resetTimer(self):
        self.timer.reset()
        self.is_running = False
        self.start_pause_btn.setText("Démarrer")
        duration = self.getSessionDuration(self.current_session)
        self.progress_widget.setProgress(duration * 60, duration * 60, self.current_session)

    def skipSession(self):
        if self.is_running:
            self.timer.reset()
        self.onSessionCompleted(self.current_session)

    def getSessionDuration(self, session_type):
        s = self.settings_widget.settings
        durations = {
            "work": s["work_duration"],
            "break": s["break_duration"],
            "long_break": s["long_break_duration"]
        }
        return durations.get(session_type, 25)

    def updateDisplay(self, remaining_time):
        duration = self.getSessionDuration(self.current_session)
        self.progress_widget.setProgress(remaining_time, duration * 60, self.current_session)

    def onSessionCompleted(self, session_type):
        self.is_running = False
        self.start_pause_btn.setText("Démarrer")
        duration = self.getSessionDuration(session_type)
        self.history_widget.addSession(session_type, duration * 60, datetime.now())
        if session_type == "work":
            self.session_count += 1
            if self.session_count % self.settings_widget.settings["sessions_until_long_break"] == 0:
                self.current_session = "long_break"
            else:
                self.current_session = "break"
        else:
            self.current_session = "work"
        should_auto = (
            (self.current_session == "work" and self.settings_widget.settings["auto_start_work"]) or
            (self.current_session in ["break","long_break"] and self.settings_widget.settings["auto_start_breaks"])
        )
        if should_auto:
            QTimer.singleShot(2000, self.startCurrentSession)
        else:
            self.resetTimer()
        self.updateSessionInfo()

    def updateSessionInfo(self):
        session_names = {"work":"Séance de travail", "break":"Pause courte", "long_break":"Pause longue"}
        if self.is_running:
            self.session_info.setText(f"{session_names[self.current_session]} en cours…")
        else:
            self.session_info.setText(f"Prêt pour : {session_names[self.current_session]}")

    def applySettings(self, settings):
        self.progress_widget.setTheme(settings["theme"])
        if not self.is_running:
            self.resetTimer()
        if settings.get("mode_zen",False):
            self.progress_widget.setTheme("zen")
            self.setStyleSheet("QMainWindow{background:#f9f6ef;}")
        else:
            self.setStyleSheet("QMainWindow{background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F8F9FA, stop:1 #E9ECEF);}")

    def loadSettings(self):
        try:
            with open("pomodoro_settings.json", "r") as f:
                settings = json.load(f)
                self.settings_widget.settings.update(settings)
                self.settings_widget.work_spin.setValue(settings.get("work_duration", 25))
                self.settings_widget.break_spin.setValue(settings.get("break_duration", 5))
                self.settings_widget.long_break_spin.setValue(settings.get("long_break_duration", 15))
                self.settings_widget.sessions_spin.setValue(settings.get("sessions_until_long_break", 4))
                self.settings_widget.theme_combo.setCurrentText(settings.get("theme", "modern"))
                self.applySettings(settings)
        except Exception as e:
            print(f"Erreur lors du chargement : {e}")

    def saveSettings(self):
        try:
            with open("pomodoro_settings.json", "w") as f:
                json.dump(self.settings_widget.settings, f)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")

    def closeEvent(self, event):
        self.saveSettings()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = PomodoroApp()
    window.show()
    sys.exit(app.exec())