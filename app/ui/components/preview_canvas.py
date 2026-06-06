from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QToolBar, QStackedWidget
from PyQt6.QtGui import QActionGroup
from PyQt6.QtCore import Qt, QSize
import qtawesome as qta
from app.canvas.pdf_canvas_view import PDFCanvasView

class PreviewCanvas(QWidget):
    def __init__(self, mode_name, scene):
        super().__init__()
        self.scene = scene
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        is_docx = mode_name == "DOCX Mode"
        
        # Toolbar Row
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(18, 18))
        
        icon_select = qta.icon('mdi6.hand-back-right', color='#D4D4D4', color_on='white', color_active='white')
        self.action_select = self.toolbar.addAction(icon_select, "")
        self.action_select.setToolTip("Select Tool")
        self.action_select.setCheckable(True)
        
        icon_text = qta.icon('mdi6.format-text', color='#D4D4D4', color_on='white', color_active='white')
        self.action_text = self.toolbar.addAction(icon_text, "")
        self.action_text.setToolTip("Text Tool")
        self.action_text.setCheckable(True)
        
        self.tool_group = QActionGroup(self)
        self.tool_group.addAction(self.action_select)
        self.tool_group.addAction(self.action_text)
        self.tool_group.setExclusive(True)
        
        self.separator1 = self.toolbar.addSeparator()
        
        icon_zoom_in = qta.icon('mdi6.magnify-plus', color='#D4D4D4', color_active='white')
        self.action_zoom_in = self.toolbar.addAction(icon_zoom_in, "")
        self.action_zoom_in.setToolTip("Zoom In")
        
        icon_zoom_out = qta.icon('mdi6.magnify-minus', color='#D4D4D4', color_active='white')
        self.action_zoom_out = self.toolbar.addAction(icon_zoom_out, "")
        self.action_zoom_out.setToolTip("Zoom Out")
        
        icon_fit = qta.icon('mdi6.fit-to-page-outline', color='#D4D4D4', color_active='white')
        self.action_fit_page = self.toolbar.addAction(icon_fit, "")
        self.action_fit_page.setToolTip("Fit Page")
        layout.addWidget(self.toolbar)
        
        if is_docx:
            self.action_select.setVisible(False)
            self.action_text.setVisible(False)
            self.separator1.setVisible(False)
        else:
            self.action_select.setChecked(True)
        
        # Center Area
        self.stacked = QStackedWidget()
        
        # Empty State Widget
        self.empty_widget = QWidget()
        self.empty_widget.setObjectName("canvasArea")
        empty_layout = QVBoxLayout(self.empty_widget)
        empty_layout.setContentsMargins(32, 32, 32, 32)
        empty_layout.setSpacing(8)

        self.empty_icon = QLabel()
        self.empty_icon.setProperty("class", "emptyStateIcon")
        self.empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_icon = qta.icon('mdi6.file-document-outline', color='#858585')
        self.empty_icon.setPixmap(empty_icon.pixmap(QSize(48, 48)))
        empty_layout.addStretch(1)
        empty_layout.addWidget(self.empty_icon)

        self.empty_label = QLabel("Import a PDF or DOCX template to begin editing")
        self.empty_label.setProperty("class", "emptyState")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(self.empty_label)

        self.empty_subtitle = QLabel(mode_name)
        self.empty_subtitle.setProperty("class", "emptyStateSubtle")
        self.empty_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(self.empty_subtitle)
        empty_layout.addStretch(1)
        
        # Canvas View Widget
        self.view = PDFCanvasView(self.scene)
        self.view.setObjectName("canvasArea")
        
        self.stacked.addWidget(self.empty_widget)
        self.stacked.addWidget(self.view)
        
        layout.addWidget(self.stacked, 1)
        
        # Connect actions
        self.action_zoom_in.triggered.connect(self._on_zoom_in)
        self.action_zoom_out.triggered.connect(self._on_zoom_out)
        self.action_fit_page.triggered.connect(self._on_fit_page)
        
        self.action_select.triggered.connect(self._on_select_tool)
        self.action_text.triggered.connect(self._on_text_tool)
        
    def _clear_tools(self):
        if self.tool_group.checkedAction():
            self.tool_group.setExclusive(False)
            self.action_select.setChecked(False)
            self.action_text.setChecked(False)
            self.tool_group.setExclusive(True)
        self.scene.set_tool("hand")

    def _on_zoom_in(self):
        self._clear_tools()
        self.view.zoom_in()
        
    def _on_zoom_out(self):
        self._clear_tools()
        self.view.zoom_out()
        
    def _on_fit_page(self):
        self._clear_tools()
        self.view.fit_to_scene()

    def _on_select_tool(self):
        self.scene.set_tool("hand")
        
    def _on_text_tool(self):
        self.scene.set_tool("text")
    def show_preview(self):
        self.stacked.setCurrentWidget(self.view)
        self.view.fit_to_scene()
        
    def show_message(self, msg):
        self.empty_label.setText(msg or "Import a PDF or DOCX template to begin editing")
        self.stacked.setCurrentWidget(self.empty_widget)
