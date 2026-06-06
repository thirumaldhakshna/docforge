from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QRadioButton, QButtonGroup, QFrame

class ExportSettingsCard(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 0)
        layout.setSpacing(8)
        
        title = QLabel("EXPORT SETTINGS")
        title.setProperty("class", "CardTitle")
        layout.addWidget(title)
        
        panel = QFrame()
        panel.setObjectName("exportConfigPanel")
        content_layout = QVBoxLayout(panel)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(16)
        
        # Export Type Group
        type_group_box = QFrame()
        type_layout = QVBoxLayout(type_group_box)
        type_layout.setContentsMargins(0, 0, 0, 0)
        type_layout.setSpacing(6)
        
        type_label = QLabel("EXPORT TYPE")
        type_label.setProperty("class", "FieldGroupTitle")
        type_layout.addWidget(type_label)
        
        self.type_group = QButtonGroup(self)
        self.radio_separate = QRadioButton("Separate Documents")
        self.radio_separate.setChecked(True)
        self.radio_combined = QRadioButton("Combined Document")
        
        self.type_group.addButton(self.radio_separate)
        self.type_group.addButton(self.radio_combined)
        
        type_layout.addWidget(self.radio_separate)
        type_layout.addWidget(self.radio_combined)
        
        content_layout.addWidget(type_group_box)
        
        # Output Format Group
        format_group_box = QFrame()
        format_layout = QVBoxLayout(format_group_box)
        format_layout.setContentsMargins(0, 0, 0, 0)
        format_layout.setSpacing(6)
        
        format_label = QLabel("OUTPUT FORMAT")
        format_label.setProperty("class", "FieldGroupTitle")
        format_layout.addWidget(format_label)
        
        self.format_group = QButtonGroup(self)
        self.radio_docx = QRadioButton("DOCX")
        self.radio_docx.setChecked(True)
        self.radio_pdf = QRadioButton("PDF")
        
        self.format_group.addButton(self.radio_docx)
        self.format_group.addButton(self.radio_pdf)
        
        format_layout.addWidget(self.radio_docx)
        format_layout.addWidget(self.radio_pdf)
        
        content_layout.addWidget(format_group_box)
        
        layout.addWidget(panel)

    def set_mode(self, is_docx_mode):
        if is_docx_mode:
            self.radio_docx.setVisible(True)
            self.radio_docx.setChecked(True)
        else:
            self.radio_docx.setVisible(False)
            self.radio_pdf.setChecked(True)

    def get_export_type(self):
        return "separate" if self.radio_separate.isChecked() else "combined"
        
    def get_output_format(self):
        return "docx" if self.radio_docx.isChecked() else "pdf"
