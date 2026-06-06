from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QFrame, QCheckBox
from PyQt6.QtCore import Qt, QPoint, QSettings

class WelcomeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumWidth(500)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Container 
        self.container = QFrame()
        self.container.setFrameShape(QFrame.Shape.NoFrame)
        self.container.setObjectName("welcomeContainer")
        self.container.setStyleSheet("""
            #welcomeContainer {
                background-color: #252526;
                border: 1px solid #4A4A4A;
                border-radius: 8px;
            }
        """)
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Title Bar
        self.title_bar = QWidget()
        self.title_bar.setObjectName("welcomeDialogTitleBar")
        self.title_bar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.title_bar.setFixedHeight(30)
        self.title_bar.setStyleSheet("""
            background-color: #1E1E1E;
            border-top-left-radius: 7px;
            border-top-right-radius: 7px;
        """)
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(15, 0, 0, 0)
        title_layout.setSpacing(10)
        
        self.title_label = QLabel("Welcome to DocForge")
        self.title_label.setStyleSheet("color: white; font-size: 13px; border: none; background: transparent;")
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: white;
                font-size: 14px;
                min-width: 46px;
                max-width: 46px;
                min-height: 30px;
                max-height: 30px;
                padding: 0;
                margin: 0;
            }
            QPushButton:hover {
                background-color: #E81123;
            }
        """)
        self.btn_close.clicked.connect(self.reject)
        title_layout.addWidget(self.btn_close)
        
        container_layout.addWidget(self.title_bar)
        
        # Title divider
        title_divider = QFrame()
        title_divider.setFrameShape(QFrame.Shape.HLine)
        title_divider.setFrameShadow(QFrame.Shadow.Plain)
        title_divider.setFixedHeight(1)
        title_divider.setStyleSheet("background-color: #3E3E42; border: none; color: #3E3E42;")
        container_layout.addWidget(title_divider)
        
        # Body
        self.body_widget = QWidget()
        self.body_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.body_widget.setStyleSheet("""
            background-color: #252526;
            border-bottom-left-radius: 7px;
            border-bottom-right-radius: 7px;
        """)
        body_layout = QVBoxLayout(self.body_widget)
        body_layout.setContentsMargins(20, 20, 20, 20)
        body_layout.setSpacing(15)
        
        content = """
        <div style='color: white; font-family: "Segoe UI", sans-serif;'>
            <div align='center' style='margin-bottom: 10px;'>
                <img src='app/assets/icons/app_64.png' width='64' height='64'>
            </div>
            <p align='center' style='font-size: 16px; font-weight: bold;'>Welcome to DocForge</p>
            <p align='center' style='margin-bottom: 20px;'>DocForge helps you generate personalized PDF and DOCX documents from templates.</p>
            
            <table width="100%" cellpadding="5">
            <tr>
                <td valign="top" width="50%">
                    <b style="color: #4daafc;">Getting Started</b><br>
                    1. Import a PDF or DOCX template.<br>
                    2. Import an Excel data sheet.<br>
                    3. Place variables in the template.<br>
                    4. Configure export settings.<br>
                    5. Click Generate Documents.<br>
                    <br>
                    <b style="color: #4daafc;">Supported Variables</b><br>
                    {{name}}<br>
                    {{department}}<br>
                    {{email}}<br>
                    {{id}}
                </td>
                <td valign="top" width="50%">
                    <b style="color: #4daafc;">System Requirements</b><br>
                    • Windows 10 / Windows 11<br>
                    • Minimum 4 GB RAM<br>
                    • Recommended 8 GB RAM<br>
                    • 200 MB Free Disk Space<br>
                    <br>
                    <b style="color: #4daafc;">Tips</b><br>
                    • Save projects frequently.<br>
                    • Keep variable names consistent.<br>
                    • Verify template formatting before export.<br>
                    • Use PDF Designer Mode for visual layouts.
                </td>
            </tr>
            </table>
        </div>
        """
        
        self.text_label = QLabel(content)
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("border: none; background: transparent;")
        body_layout.addWidget(self.text_label)
        
        # Bottom Controls
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 10, 0, 0)
        
        self.dont_show_checkbox = QCheckBox("Don't show again")
        self.dont_show_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
                border: none;
                background: transparent;
            }
            QCheckBox::indicator {
                width: 13px;
                height: 13px;
            }
        """)
        bottom_layout.addWidget(self.dont_show_checkbox)
        
        bottom_layout.addStretch()
        
        self.btn_get_started = QPushButton("Get Started")
        self.btn_get_started.setStyleSheet("""
            QPushButton {
                background-color: #0E639C;
                color: white;
                border: none;
                min-width: 100px;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177BB;
            }
            QPushButton:pressed {
                background-color: #094771;
            }
        """)
        self.btn_get_started.clicked.connect(self._on_get_started)
        bottom_layout.addWidget(self.btn_get_started)
        
        body_layout.addLayout(bottom_layout)
        container_layout.addWidget(self.body_widget)
        main_layout.addWidget(self.container)
        
        self.offset = None
        
    def _on_get_started(self):
        if self.dont_show_checkbox.isChecked():
            settings = QSettings("Thirumal Dhakshnamoorthy", "DocForge")
            settings.setValue("show_welcome_screen", False)
        self.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() <= 30:
            self.offset = event.position().toPoint()
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.offset)
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = None
            super().mouseReleaseEvent(event)

    @classmethod
    def show_if_needed(cls, parent):
        settings = QSettings("Thirumal Dhakshnamoorthy", "DocForge")
        show_welcome = settings.value("show_welcome_screen", True, type=bool)
        if show_welcome:
            dlg = cls(parent)
            dlg.exec()
