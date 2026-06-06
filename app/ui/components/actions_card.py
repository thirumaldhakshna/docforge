from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QProgressBar
from PyQt6.QtCore import pyqtSignal

class ActionsCard(QWidget):
    generate_clicked = pyqtSignal()
    cancel_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 16)
        layout.setSpacing(8)
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        
        self.btn_generate = QPushButton("Generate Documents")
        self.btn_generate.setProperty("class", "primaryButton")
        self.btn_generate.setFixedHeight(44)
        self.btn_generate.clicked.connect(self.generate_clicked.emit)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setProperty("class", "secondaryButton")
        self.btn_cancel.clicked.connect(self.cancel_clicked.emit)
        self.btn_cancel.hide()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        
        content_layout.addWidget(self.btn_generate)
        content_layout.addWidget(self.btn_cancel)
        content_layout.addWidget(self.progress_bar)
        
        layout.addLayout(content_layout)
