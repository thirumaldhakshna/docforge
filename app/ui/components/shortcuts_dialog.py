from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QFrame
from PyQt6.QtCore import Qt, QPoint

class ShortcutsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumWidth(400)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Container 
        self.container = QFrame()
        self.container.setFrameShape(QFrame.Shape.NoFrame)
        self.container.setObjectName("shortcutsContainer")
        self.container.setStyleSheet("""
            #shortcutsContainer {
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
        self.title_bar.setObjectName("shortcutsDialogTitleBar")
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
        
        self.title_label = QLabel("Keyboard Shortcuts")
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
        <div style='color: white; font-family: "Segoe UI", sans-serif; font-size: 13px;'>
            <table width="100%" cellpadding="6">
                <tr><td width="30%"><b>Ctrl + N</b></td><td>New Project</td></tr>
                <tr><td><b>Ctrl + O</b></td><td>Open Project</td></tr>
                <tr><td><b>Ctrl + S</b></td><td>Save Project</td></tr>
                <tr><td colspan="2"><hr style="border-top: 1px solid #3E3E42;"></td></tr>
                <tr><td><b>Ctrl + Z</b></td><td>Undo</td></tr>
                <tr><td><b>Ctrl + Y</b></td><td>Redo</td></tr>
                <tr><td colspan="2"><hr style="border-top: 1px solid #3E3E42;"></td></tr>
                <tr><td><b>Delete</b></td><td>Delete Selected Layer</td></tr>
                <tr><td colspan="2"><hr style="border-top: 1px solid #3E3E42;"></td></tr>
                <tr><td><b>Ctrl + +</b></td><td>Zoom In</td></tr>
                <tr><td><b>Ctrl + -</b></td><td>Zoom Out</td></tr>
                <tr><td><b>Ctrl + 0</b></td><td>Fit To Page</td></tr>
            </table>
        </div>
        """
        
        self.text_label = QLabel(content)
        self.text_label.setStyleSheet("border: none; background: transparent;")
        body_layout.addWidget(self.text_label)
        
        container_layout.addWidget(self.body_widget)
        main_layout.addWidget(self.container)
        
        self.offset = None
        
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
