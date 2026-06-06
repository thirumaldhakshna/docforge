from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QMenuBar
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QPoint

class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(32)
        self.setObjectName("customTitleBar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Left: App Icon
        self.icon_label = QLabel()
        from app.utils.path_helpers import resource_path
        
        pixmap = QPixmap(resource_path("assets/icons/app.ico"))
        if not pixmap.isNull():
            self.icon_label.setPixmap(pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        self.layout.addWidget(self.icon_label)
        self.layout.addSpacing(10)
        
        # Center: Menu Bar
        self.menu_bar = QMenuBar(self)
        self.layout.addWidget(self.menu_bar)
        
        self.layout.addStretch()
        
        # Right: Buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)
        
        self.btn_min = QPushButton("—")
        self.btn_min.setObjectName("titleBarBtn")
        self.btn_min.clicked.connect(self.parent.showMinimized)
        
        self.btn_max = QPushButton("□")
        self.btn_max.setObjectName("titleBarBtn")
        self.btn_max.clicked.connect(self.toggle_max)
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("titleBarCloseBtn")
        self.btn_close.clicked.connect(self.parent.close)
        
        button_layout.addWidget(self.btn_min)
        button_layout.addWidget(self.btn_max)
        button_layout.addWidget(self.btn_close)
        
        self.layout.addLayout(button_layout)
        
        self.offset = None

    # Title label removed; title handled by TopNav now.

    def toggle_max(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.btn_max.setText("□")
        else:
            self.parent.showMaximized()
            self.btn_max.setText("❐")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = event.position().toPoint()
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.MouseButton.LeftButton:
            if self.parent.isMaximized():
                self.toggle_max()
                self.offset = QPoint(self.width() // 2, 10)
            self.parent.move(event.globalPosition().toPoint() - self.offset)
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = None
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_max()
            super().mouseDoubleClickEvent(event)
