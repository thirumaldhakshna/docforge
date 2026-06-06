from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QFrame, QProgressBar
from PyQt6.QtCore import Qt, QPoint, QSize
import qtawesome as qta
import os

class CustomDialog(QDialog):
    # Constants mimicking QMessageBox standard buttons
    Ok = 1
    Save = 2
    Discard = 4
    Cancel = 8
    Yes = 16
    No = 32

    def __init__(self, parent=None, title="", text="", buttons=Ok, default_button=Ok, icon=None, details=None, saved_to=None, center_buttons=False):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumWidth(420)
        
        self.clicked_button = None
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Container — use QFrame so CSS border actually renders
        self.container = QFrame()
        self.container.setObjectName("dialogContainer")
        self.container.setFrameShape(QFrame.Shape.NoFrame)
        self.container.setStyleSheet("""
            #dialogContainer {
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
        self.title_bar.setObjectName("customDialogTitleBar")
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
        
        self.title_label = QLabel(title)
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
        
        # Title divider — dedicated QFrame line
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
        body_layout.setContentsMargins(24, 24, 24, 20)
        body_layout.setSpacing(18)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        self.icon_label = None
        if icon:
            self.icon_label = QLabel()
            self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_name = 'mdi6.check-circle' if icon == "success" else 'mdi6.alert-circle'
            icon_color = '#3FB950' if icon == "success" else '#F85149'
            self.icon_label.setPixmap(qta.icon(icon_name, color=icon_color).pixmap(QSize(44, 44)))
            self.icon_label.setStyleSheet("border: none; background: transparent;")
            content_layout.addWidget(self.icon_label)
        
        self.text_label = QLabel(text)
        self.text_label.setWordWrap(True)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter if icon else Qt.AlignmentFlag.AlignLeft)
        self.text_label.setStyleSheet("color: white; font-size: 13px; border: none; background: transparent; line-height: 150%;")
        content_layout.addWidget(self.text_label)

        if saved_to:
            path_title = QLabel("Saved to")
            path_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            path_title.setStyleSheet("color: #A0A0A0; font-size: 11px; font-weight: 700; border: none; background: transparent;")
            content_layout.addWidget(path_title)

            path_frame = QFrame()
            path_frame.setStyleSheet("""
                QFrame {
                    background-color: #1E1E1E;
                    border: 1px solid #3E3E42;
                    border-radius: 4px;
                }
            """)
            path_layout = QHBoxLayout(path_frame)
            path_layout.setContentsMargins(12, 10, 12, 10)
            path_layout.setSpacing(10)

            path_icon = QLabel()
            path_icon.setPixmap(qta.icon('mdi6.folder-outline', color='#C5C5C5').pixmap(QSize(18, 18)))
            path_icon.setStyleSheet("border: none; background: transparent;")
            path_icon.setAlignment(Qt.AlignmentFlag.AlignTop)
            path_layout.addWidget(path_icon)

            path_text = self._format_saved_path(saved_to)
            self.saved_path_label = QLabel(path_text)
            self.saved_path_label.setWordWrap(True)
            self.saved_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            self.saved_path_label.setStyleSheet("color: #D4D4D4; font-size: 12px; border: none; background: transparent;")
            path_layout.addWidget(self.saved_path_label, 1)

            content_layout.addWidget(path_frame)

        if details:
            details_frame = QFrame()
            details_frame.setStyleSheet("""
                QFrame {
                    background-color: #1E1E1E;
                    border: 1px solid #3E3E42;
                    border-radius: 4px;
                }
            """)
            details_layout = QVBoxLayout(details_frame)
            details_layout.setContentsMargins(12, 10, 12, 10)
            details_layout.setSpacing(6)

            details_title = QLabel("Details")
            details_title.setStyleSheet("color: #A0A0A0; font-size: 11px; font-weight: 700; border: none; background: transparent;")
            details_layout.addWidget(details_title)

            details_label = QLabel(details)
            details_label.setWordWrap(True)
            details_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            details_label.setStyleSheet("color: #CCCCCC; font-size: 12px; border: none; background: transparent;")
            details_layout.addWidget(details_label)
            content_layout.addWidget(details_frame)

        body_layout.addLayout(content_layout)
        
        # Buttons
        button_box = QHBoxLayout()
        button_box.addStretch()
        button_box.setSpacing(10)
        
        self.buttons_dict = {}
        
        btn_style = """
            QPushButton {
                background-color: #3C3C3C;
                color: white;
                border: 1px solid #5A5A5A;
                min-width: 90px;
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
            QPushButton:pressed {
                background-color: #007ACC;
            }
        """
        primary_btn_style = """
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: 1px solid #007ACC;
                min-width: 90px;
                padding: 7px 14px;
                border-radius: 4px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0E639C;
                border-color: #0E639C;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
        """
        
        def create_btn(text, val):
            btn = QPushButton(text)
            btn.setStyleSheet(primary_btn_style if val == default_button else btn_style)
            btn.setMinimumWidth(120 if center_buttons and val == default_button else 80)
            btn.clicked.connect(lambda _, v=val: self.finish(v))
            button_box.addWidget(btn)
            self.buttons_dict[val] = btn
            if val == default_button:
                btn.setDefault(True)
                btn.setFocus()
                
        if buttons & self.Save:
            create_btn("Save", self.Save)
        if buttons & self.Discard:
            create_btn("Discard", self.Discard)
        if buttons & self.Yes:
            create_btn("Yes", self.Yes)
        if buttons & self.No:
            create_btn("No", self.No)
        if buttons & self.Ok:
            create_btn("OK", self.Ok)
        if buttons & self.Cancel:
            create_btn("Cancel", self.Cancel)

        if center_buttons:
            button_box.addStretch()
            
        body_layout.addLayout(button_box)
        container_layout.addWidget(self.body_widget)
        main_layout.addWidget(self.container)
        
        self.offset = None

    def finish(self, val):
        self.clicked_button = val
        self.accept()

    @staticmethod
    def _format_saved_path(path):
        normalized = os.path.normpath(str(path))
        display_path = normalized.replace("/", "\\")
        folder, filename = os.path.split(display_path)

        if filename and os.path.splitext(filename)[1]:
            if folder:
                return f"{folder}\\\n{filename}"
            return filename

        return display_path

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
    def information(cls, parent, title, text):
        dlg = cls(parent, title, text, cls.Ok, cls.Ok)
        dlg.exec()
        return cls.Ok

    @classmethod
    def export_success(cls, parent, saved_to=None):
        text = "Document generated successfully"
        dlg = cls(parent, "Export Complete", text, cls.Ok, cls.Ok, icon="success", saved_to=saved_to, center_buttons=True)
        dlg.exec()
        return cls.Ok

    @classmethod
    def export_failed(cls, parent, details=None):
        text = "Unable to generate the document.\n\nPlease check the template and data source, then try again."
        dlg = cls(parent, "Export Failed", text, cls.Ok, cls.Ok, icon="error", details=details)
        dlg.exec()
        return cls.Ok

    @classmethod
    def warning(cls, parent, title, text):
        dlg = cls(parent, title, text, cls.Ok, cls.Ok)
        dlg.exec()
        return cls.Ok

    @classmethod
    def critical(cls, parent, title, text):
        dlg = cls(parent, title, text, cls.Ok, cls.Ok)
        dlg.exec()
        return cls.Ok

    @classmethod
    def question(cls, parent, title, text, buttons, default_button):
        dlg = cls(parent, title, text, buttons, default_button)
        dlg.exec()
        return dlg.clicked_button or cls.Cancel

    @classmethod
    def about(cls, parent, title, text):
        dlg = cls(parent, title, text, cls.Ok, cls.Ok, center_buttons=True)
        dlg.exec()
        return cls.Ok


class ExportProgressDialog(QDialog):
    def __init__(self, parent=None, stage_label="Generating PDF"):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(440)

        self.stages = [
            "Reading template",
            "Loading data source",
            "Replacing variables",
            stage_label,
            "Saving file"
        ]
        self.stage_labels = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        container = QFrame()
        container.setObjectName("progressContainer")
        container.setFrameShape(QFrame.Shape.NoFrame)
        container.setStyleSheet("""
            #progressContainer {
                background-color: #252526;
                border: 1px solid #4A4A4A;
                border-radius: 8px;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        title_bar = QWidget()
        title_bar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        title_bar.setFixedHeight(34)
        title_bar.setStyleSheet("""
            background-color: #1E1E1E;
            border-top-left-radius: 7px;
            border-top-right-radius: 7px;
        """)

        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 0, 15, 0)
        title_layout.setSpacing(10)

        title_label = QLabel("Exporting Document")
        title_label.setStyleSheet("color: white; font-size: 13px; font-weight: 600; border: none; background: transparent;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        container_layout.addWidget(title_bar)

        title_divider = QFrame()
        title_divider.setFrameShape(QFrame.Shape.HLine)
        title_divider.setFrameShadow(QFrame.Shadow.Plain)
        title_divider.setFixedHeight(1)
        title_divider.setStyleSheet("background-color: #3E3E42; border: none; color: #3E3E42;")
        container_layout.addWidget(title_divider)

        body = QWidget()
        body.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        body.setStyleSheet("""
            background-color: #252526;
            border-bottom-left-radius: 7px;
            border-bottom-right-radius: 7px;
        """)
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(28, 26, 28, 24)
        body_layout.setSpacing(18)

        self.message_label = QLabel("Generating output...")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("color: white; font-size: 14px; font-weight: 600; border: none; background: transparent;")
        body_layout.addWidget(self.message_label)

        stages_frame = QFrame()
        stages_frame.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border: 1px solid #3E3E42;
                border-radius: 4px;
            }
        """)
        stages_layout = QVBoxLayout(stages_frame)
        stages_layout.setContentsMargins(14, 12, 14, 12)
        stages_layout.setSpacing(8)

        for stage in self.stages:
            label = QLabel(f"□ {stage}")
            label.setStyleSheet("color: #A0A0A0; font-size: 12px; border: none; background: transparent;")
            stages_layout.addWidget(label)
            self.stage_labels.append(label)

        body_layout.addWidget(stages_frame)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3E3E42;
                background-color: #1E1E1E;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: #007ACC;
                border-radius: 5px;
            }
        """)
        body_layout.addWidget(self.progress_bar)

        self.percent_label = QLabel("0%")
        self.percent_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.percent_label.setStyleSheet("color: #D4D4D4; font-size: 13px; font-weight: 600; border: none; background: transparent;")
        body_layout.addWidget(self.percent_label)

        self.subtext_label = QLabel("Please wait while your document is being generated.")
        self.subtext_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtext_label.setWordWrap(True)
        self.subtext_label.setStyleSheet("color: #A0A0A0; font-size: 12px; border: none; background: transparent;")
        body_layout.addWidget(self.subtext_label)

        container_layout.addWidget(body)
        main_layout.addWidget(container)

        self.set_progress(0, 100)

    def show_centered(self):
        self.show()
        self.raise_()
        self.activateWindow()
        self._center_on_parent()

    def _center_on_parent(self):
        parent = self.parentWidget()
        if not parent:
            return
        parent_rect = parent.frameGeometry()
        own_rect = self.frameGeometry()
        own_rect.moveCenter(parent_rect.center())
        self.move(own_rect.topLeft())

    def set_progress(self, current, total):
        total = max(total, 1)
        percent = max(0, min(100, int(round((current / total) * 100))))
        self.progress_bar.setValue(percent)
        self.percent_label.setText(f"{percent}%")
        self._update_stages(percent)

    def _update_stages(self, percent):
        active_index = min(len(self.stage_labels) - 1, max(0, percent // 25))
        for index, label in enumerate(self.stage_labels):
            stage = self.stages[index]
            if index < active_index or percent == 100:
                label.setText(f"✓ {stage}")
                label.setStyleSheet("color: #3FB950; font-size: 12px; border: none; background: transparent;")
            elif index == active_index:
                label.setText(f"⟳ {stage}")
                label.setStyleSheet("color: #D4D4D4; font-size: 12px; font-weight: 600; border: none; background: transparent;")
            else:
                label.setText(f"□ {stage}")
                label.setStyleSheet("color: #A0A0A0; font-size: 12px; border: none; background: transparent;")
