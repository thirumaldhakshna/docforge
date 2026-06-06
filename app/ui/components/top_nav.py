from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QButtonGroup
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap

class TopNav(QWidget):
    mode_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setObjectName("topNav")
        self.setFixedHeight(38)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(0)
        
        # Left Side (Logo)
        left_container = QWidget()
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)  # 10px spacing
        
        logo_label = QLabel()
        pixmap = QPixmap("app/assets/icons/app_64.png")
        if not pixmap.isNull():
            # scale logo to 28x28
            scaled_pixmap = pixmap.scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            
        left_layout.addWidget(logo_label)
        
        self.app_logo_text = QLabel("DocForge")
        self.app_logo_text.setObjectName("appLogo")
        self.app_logo_text.setStyleSheet("font-size: 19px; font-weight: bold; color: white;")
        left_layout.addWidget(self.app_logo_text)
        
        left_layout.addStretch()
        
        # Center (Mode Tabs)
        center_container = QWidget()
        center_layout = QHBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        
        self.btn_group = QButtonGroup(self)
        
        self.btn_docx = QPushButton("DOCX Mode")
        self.btn_docx.setProperty("class", "navButton")
        self.btn_docx.setCheckable(True)
        self.btn_docx.setChecked(True)
        
        self.btn_pdf = QPushButton("PDF Designer Mode")
        self.btn_pdf.setProperty("class", "navButton")
        self.btn_pdf.setCheckable(True)
        
        self.btn_group.addButton(self.btn_docx, 0)
        self.btn_group.addButton(self.btn_pdf, 1)
        self.btn_group.buttonClicked.connect(self._on_mode_changed)
        
        center_layout.addWidget(self.btn_docx)
        center_layout.addWidget(self.btn_pdf)
        
        # Right Side (Empty spacer)
        right_container = QWidget()
        
        layout.addWidget(left_container, 1)
        layout.addWidget(center_container, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(right_container, 1)

    def _on_mode_changed(self, button):
        self.mode_changed.emit(self.btn_group.id(button))

    def set_title(self, title):
        self.app_logo_text.setText(title)
