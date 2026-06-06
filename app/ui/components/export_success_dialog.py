from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QFrame
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
import os

class ExportSuccessDialog(QDialog):
    def __init__(self, parent, output_path, doc_count, export_format, export_mode):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumWidth(450)
        
        self.output_path = output_path
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Container
        self.container = QFrame()
        self.container.setFrameShape(QFrame.Shape.NoFrame)
        self.container.setObjectName("exportSuccessContainer")
        self.container.setStyleSheet("""
            #exportSuccessContainer {
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
        self.title_bar.setObjectName("exportDialogTitleBar")
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
        
        self.title_icon = QLabel()
        from PyQt6.QtGui import QPixmap
        pixmap = QPixmap("app/assets/icons/app_64.png")
        if not pixmap.isNull():
            self.title_icon.setPixmap(pixmap.scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        title_layout.addWidget(self.title_icon)
        
        self.title_label = QLabel("Export Completed")
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
        body_layout.setContentsMargins(20, 25, 20, 25)
        body_layout.setSpacing(15)
        
        success_msg = "Combined document generated successfully" if export_mode == "Combined Document" else "Documents generated successfully"
        
        clean_path = os.path.normpath(output_path).replace('/', '\\')
        
        if os.path.isfile(clean_path) or (not os.path.isdir(clean_path) and clean_path.lower().endswith(('.pdf', '.docx'))):
            folder_raw = os.path.dirname(clean_path)
            file = os.path.basename(clean_path)
        else:
            folder_raw = clean_path
            file = ""
            
        def elide_path(p, max_len=45):
            if len(p) <= max_len: return p
            parts = p.split('\\')
            if len(parts) > 3:
                return f"{parts[0]}\\{parts[1]}\\...\\{parts[-1]}"
            return p[:20] + "..." + p[-20:]
            
        elided_folder = elide_path(folder_raw)
        
        self.folder_path = folder_raw
        
        if file:
            path_display = f"""
            <div style='color: #AAAAAA; font-size: 13px; margin-bottom: 2px;'>Folder:</div>
            <div style='color: #4daafc; font-size: 12px; margin-bottom: 10px; word-break: break-all;'>{elided_folder}</div>
            
            <div style='color: #AAAAAA; font-size: 13px; margin-bottom: 2px;'>File:</div>
            <div style='color: #4daafc; font-size: 12px; word-break: break-all;'>{file}</div>
            """
        else:
            path_display = f"""
            <div style='color: #AAAAAA; font-size: 13px; margin-bottom: 2px;'>Folder:</div>
            <div style='color: #4daafc; font-size: 12px; word-break: break-all;'>{elided_folder}</div>
            """
        
        content = f"""
        <div style='font-family: "Segoe UI", sans-serif; text-align: center;'>
            <div style='color: #3FB950; font-size: 48px; margin-bottom: 5px; font-weight: bold;'>✓</div>
            <div style='color: white; font-size: 14px; margin-bottom: 20px;'>{success_msg}</div>
            
            <div style='color: #E2E2E2; font-size: 13px; margin-bottom: 10px; font-weight: bold;'>Saved to</div>
            {path_display}
        </div>
        """
        
        self.text_label = QLabel(content)
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("border: none; background: transparent;")
        body_layout.addWidget(self.text_label)
        
        body_layout.addSpacing(10)
        
        # Bottom Controls
        button_box = QHBoxLayout()
        button_box.addStretch()
        button_box.setSpacing(10)
        
        self.btn_open = QPushButton("Open Folder")
        self.btn_open.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: white;
                border: 1px solid #555555;
                min-width: 120px;
                min-height: 32px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #444444; }
            QPushButton:pressed { background-color: #222222; }
        """)
        self.btn_open.clicked.connect(self._open_folder)
        button_box.addWidget(self.btn_open)
        
        self.btn_ok = QPushButton("OK")
        self.btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #0E639C;
                color: white;
                border: none;
                min-width: 120px;
                min-height: 32px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1177BB; }
            QPushButton:pressed { background-color: #094771; }
        """)
        self.btn_ok.clicked.connect(self.accept)
        button_box.addWidget(self.btn_ok)
        
        button_box.addStretch()
        
        body_layout.addLayout(button_box)
        container_layout.addWidget(self.body_widget)
        main_layout.addWidget(self.container)
        
        self.offset = None

    def _open_folder(self):
        folder_url = QUrl.fromLocalFile(self.folder_path)
        QDesktopServices.openUrl(folder_url)
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
