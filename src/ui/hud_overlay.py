#!/usr/bin/env python3
"""
🕉️ Saarthika Ambient Desktop HUD Overlay
A sleek, frameless, translucent circular widget with dynamic glowing states:
  - Listening (Pulsing Cyan)
  - Thinking (Spinning Purple/Magenta Arc)
  - Speaking (Vibrating Emerald Wave)
  - Idle (Soft Ambient Glass)
"""

import sys
import math
import threading
from typing import Optional

try:
    from PySide6.QtCore import Qt, QTimer, QPoint, Signal, QObject
    from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient, QFont
    from PySide6.QtWidgets import QApplication, QWidget
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False


class HUDStateBridge(QObject if PYSIDE_AVAILABLE else object):
    """Bridge for thread-safe state updates from async loops to the Qt UI."""
    if PYSIDE_AVAILABLE:
        state_changed = Signal(str)

    def __init__(self):
        if PYSIDE_AVAILABLE:
            super().__init__()


class SaarthikaHUD(QWidget if PYSIDE_AVAILABLE else object):
    """
    Frameless, translucent floating desktop widget.
    Can be dragged across the screen or double-clicked to toggle stay-on-top/click-through.
    """
    def __init__(self, size: int = 160, parent: Optional[QWidget] = None):
        if not PYSIDE_AVAILABLE:
            raise ImportError("PySide6 is required to run SaarthikaHUD. Install with: pip install PySide6")
        
        super().__init__(parent)
        self.hud_size = size
        self.state = "idle"  # idle, listening, thinking, speaking
        self.anim_phase = 0.0
        self.drag_position = QPoint()

        # Window styling
        self.setFixedSize(self.hud_size, self.hud_size)
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.SubWindow
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)

        # Position in bottom-right corner by default
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.hud_size - 40, screen.height() - self.hud_size - 60)

        # Animation timer (60 FPS refresh)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_animation)
        self.timer.start(16)  # ~60 FPS

    def set_state(self, new_state: str):
        """Update state (idle, listening, thinking, speaking)."""
        self.state = new_state.lower().strip()
        self.update()

    def _update_animation(self):
        self.anim_phase += 0.06
        if self.anim_phase > 2 * math.pi:
            self.anim_phase -= 2 * math.pi
        self.update()

    # Drag window handlers
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center_x = self.width() / 2
        center_y = self.height() / 2
        radius = (self.width() / 2) - 15

        # Color schemes based on assistant state
        if self.state == "listening":
            # Pulsing Cyan
            pulse = 0.85 + 0.15 * math.sin(self.anim_phase * 2)
            glow_col = QColor(0, 230, 255, int(180 * pulse))
            ring_col = QColor(0, 210, 255, 230)
            inner_col = QColor(10, 40, 60, 160)
            label = "LISTENING"
            label_col = QColor(180, 245, 255)
        elif self.state == "thinking":
            # Spinning Purple / Magenta
            glow_col = QColor(210, 60, 255, 170)
            ring_col = QColor(230, 80, 255, 240)
            inner_col = QColor(50, 15, 60, 170)
            label = "THINKING"
            label_col = QColor(245, 190, 255)
        elif self.state == "speaking":
            # Vibrating Emerald Green
            vibe = 0.8 + 0.2 * math.sin(self.anim_phase * 4)
            glow_col = QColor(0, 255, 150, int(190 * vibe))
            ring_col = QColor(50, 255, 170, 240)
            inner_col = QColor(10, 50, 30, 160)
            label = "SPEAKING"
            label_col = QColor(190, 255, 220)
        else:
            # Soft Ambient Glass (Idle)
            breath = 0.6 + 0.15 * math.sin(self.anim_phase)
            glow_col = QColor(80, 140, 220, int(90 * breath))
            ring_col = QColor(100, 160, 240, 150)
            inner_col = QColor(20, 25, 35, 140)
            label = "SAARTHIKA"
            label_col = QColor(170, 190, 220)

        # 1. Outer Radial Glow
        glow_grad = QRadialGradient(center_x, center_y, radius + 12)
        glow_grad.setColorAt(0.7, glow_col)
        glow_grad.setColorAt(1.0, QColor(glow_col.red(), glow_col.green(), glow_col.blue(), 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(glow_grad))
        painter.drawEllipse(center_x - radius - 12, center_y - radius - 12, (radius + 12) * 2, (radius + 12) * 2)

        # 2. Dark Glassy Core
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(inner_col))
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)

        # 3. Dynamic Outer Arcs
        if self.state == "thinking":
            # Dual rotating orbit arcs
            rot_deg = math.degrees(self.anim_phase * 1.5) % 360
            pen = QPen(ring_col, 3.5)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawArc(center_x - radius, center_y - radius, radius * 2, radius * 2, int(rot_deg * 16), 110 * 16)
            painter.drawArc(center_x - radius, center_y - radius, radius * 2, radius * 2, int((rot_deg + 180) * 16), 110 * 16)
        else:
            # Continuous ring with gentle breath
            pen = QPen(ring_col, 2.5)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)

        # 4. Center Label & Logo
        painter.setPen(label_col)
        font = QFont("Sans-Serif", 9, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, label)


class HUDController:
    """Helper to launch and control the HUD safely across threads."""
    def __init__(self):
        self.hud_window: Optional[SaarthikaHUD] = None
        self.bridge: Optional[HUDStateBridge] = None
        self.thread: Optional[threading.Thread] = None

    def start(self):
        """Starts Qt application loop in a dedicated background thread."""
        if not PYSIDE_AVAILABLE:
            print("⚠️  HUD disabled: PySide6 is not installed.")
            return False

        ready_event = threading.Event()

        def _run_qt():
            app = QApplication.instance()
            if not app:
                app = QApplication(sys.argv)
            
            self.bridge = HUDStateBridge()
            self.hud_window = SaarthikaHUD()
            self.bridge.state_changed.connect(self.hud_window.set_state)
            self.hud_window.show()
            ready_event.set()
            app.exec()

        self.thread = threading.Thread(target=_run_qt, daemon=True)
        self.thread.start()
        ready_event.wait(timeout=3)
        return True

    def set_state(self, state: str):
        """Thread-safe update of the HUD state."""
        if self.bridge and PYSIDE_AVAILABLE:
            self.bridge.state_changed.emit(state)


if __name__ == "__main__":
    if not PYSIDE_AVAILABLE:
        print("Install PySide6 with: pip install PySide6")
        sys.exit(1)

    import time
    app = QApplication(sys.argv)
    hud = SaarthikaHUD()
    hud.show()

    # Demo cycle states
    states = ["idle", "listening", "thinking", "speaking"]
    idx = [0]

    def cycle():
        idx[0] = (idx[0] + 1) % len(states)
        hud.set_state(states[idx[0]])

    demo_timer = QTimer()
    demo_timer.timeout.connect(cycle)
    demo_timer.start(2500)

    sys.exit(app.exec())

