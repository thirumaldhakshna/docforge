from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import pyqtSignal

class TypographyCard(QWidget):
    font_changed = pyqtSignal(str)
    size_changed = pyqtSignal(int)
    bold_toggled = pyqtSignal(bool)
    italic_toggled = pyqtSignal(bool)
    color_changed = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.is_updating_ui = False
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        title = QLabel("TYPOGRAPHY")
        title.setProperty("class", "CardTitle")
        layout.addWidget(title)
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        
        self.font_family = QComboBox()
        self.font_family.addItems(["Times New Roman", "Cambria", "Calibri", "Arial", "Arial Black", "Verdana", "Tahoma", "Segoe UI"])
        self.font_family.setCurrentText("Times New Roman")
        self.font_family.currentTextChanged.connect(self._on_font_changed)
        content_layout.addWidget(self.font_family)
        
        self.font_size = QComboBox()
        self.font_size.addItems(["10", "12", "14", "16", "24", "32", "48", "64"])
        self.font_size.setCurrentText("14")
        self.font_size.currentTextChanged.connect(self._on_size_changed)
        content_layout.addWidget(self.font_size)
        
        tools_layout = QHBoxLayout()
        tools_layout.setContentsMargins(0, 0, 0, 0)
        tools_layout.setSpacing(8)
        self.btn_bold = QPushButton("B")
        self.btn_bold.setProperty("class", "secondaryButton")
        self.btn_bold.setCheckable(True)
        self.btn_bold.toggled.connect(self._on_bold_toggled)
        
        self.btn_italic = QPushButton("I")
        self.btn_italic.setProperty("class", "secondaryButton")
        self.btn_italic.setCheckable(True)
        self.btn_italic.toggled.connect(self._on_italic_toggled)
        
        self.btn_color = QPushButton("Color")
        self.btn_color.setProperty("class", "secondaryButton")
        self.btn_color.clicked.connect(self._on_color_clicked)
        
        tools_layout.addWidget(self.btn_bold)
        tools_layout.addWidget(self.btn_italic)
        tools_layout.addWidget(self.btn_color)
        
        content_layout.addLayout(tools_layout)
        layout.addLayout(content_layout)

    def _on_font_changed(self, text):
        if not self.is_updating_ui:
            self.font_changed.emit(text)

    def _on_size_changed(self, text):
        if not self.is_updating_ui:
            try:
                self.size_changed.emit(int(text))
            except ValueError:
                pass

    def _on_bold_toggled(self, checked):
        if not self.is_updating_ui:
            self.bold_toggled.emit(checked)

    def _on_italic_toggled(self, checked):
        if not self.is_updating_ui:
            self.italic_toggled.emit(checked)

    def _on_color_clicked(self):
        from PyQt6.QtWidgets import QColorDialog
        color = QColorDialog.getColor()
        if color.isValid():
            if not self.is_updating_ui:
                self.color_changed.emit(color)

    def update_from_layer(self, layer):
        self.is_updating_ui = True
        if layer:
            font = layer.font()
            
            idx = self.font_family.findText(font.family())
            if idx >= 0:
                self.font_family.setCurrentIndex(idx)
                
            size_str = str(font.pointSize())
            idx = self.font_size.findText(size_str)
            if idx >= 0:
                self.font_size.setCurrentIndex(idx)
            else:
                self.font_size.setCurrentText(size_str)
                
            self.btn_bold.setChecked(font.bold())
            self.btn_italic.setChecked(font.italic())
            
            self.setEnabled(True)
        else:
            self.setEnabled(False)
            
        self.is_updating_ui = False
