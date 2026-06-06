from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal, QStandardPaths
import os

class UploadCard(QWidget):
    template_uploaded = pyqtSignal(str)
    excel_uploaded = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        
        self.last_template_dir = ""
        self.last_excel_dir = ""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 0)
        layout.setSpacing(8)
        
        title = QLabel("DOCUMENTS")
        title.setProperty("class", "CardTitle")
        layout.addWidget(title)
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        
        self.btn_template = QPushButton("Import Template")
        self.btn_template.setProperty("class", "primaryButton")
        self.btn_template.clicked.connect(self._on_upload_template)
        content_layout.addWidget(self.btn_template)
        
        self.btn_excel = QPushButton("Import Data Sheet")
        self.btn_excel.setProperty("class", "secondaryButton")
        self.btn_excel.clicked.connect(self._on_upload_excel)
        content_layout.addWidget(self.btn_excel)
        
        layout.addLayout(content_layout)

    def _get_start_dir(self, last_dir):
        if last_dir and os.path.exists(last_dir):
            return last_dir
        return QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)

    def _on_upload_template(self):
        start_dir = self._get_start_dir(self.last_template_dir)
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Template",
            start_dir,
            "Documents (*.pdf *.docx);;All Files (*)"
        )
        if file_path:
            self.last_template_dir = os.path.dirname(file_path)
            self.template_uploaded.emit(file_path)

    def _on_upload_excel(self):
        start_dir = self._get_start_dir(self.last_excel_dir)
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Excel",
            start_dir,
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        if file_path:
            self.last_excel_dir = os.path.dirname(file_path)
            self.excel_uploaded.emit(file_path)
