import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QSplitter, QStackedWidget,
    QMenuBar, QMenu, QFileDialog, QApplication, QLabel, QFrame, QHBoxLayout
)
from PyQt6.QtGui import QAction, QUndoStack, QDesktopServices, QIcon
from PyQt6.QtCore import Qt, QTimer, QStandardPaths, QUrl, QSettings
from app.editor.commands import (
    PropertyChangeCommand, DeleteLayerCommand, AddLayerCommand
)
from PyQt6.QtCore import Qt
from app.themes.style import get_stylesheet
from app.ui.components.top_nav import TopNav
from app.ui.components.upload_card import UploadCard
from app.ui.components.fields_card import FieldsCard
from app.ui.components.typography_card import TypographyCard
from app.ui.components.export_settings_card import ExportSettingsCard
from app.ui.components.actions_card import ActionsCard
from app.ui.components.preview_canvas import PreviewCanvas
from app.canvas.preview_scene import PreviewScene
from app.canvas.preview_controller import PreviewController
from app.editor.items.text_layer_item import TextLayerItem
from app.services.excel_service import ExcelService
from app.services.variable_service import VariableService
from app.services.docx_variable_service import DocxVariableService
from app.services.project_service import ProjectService
from app.ui.components.custom_dialog import CustomDialog, ExportProgressDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DocForge")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(1400, 850)
        self.setStyleSheet(get_stylesheet())
        
        self.current_project_path = None
        self.is_dirty = False
        self.last_project_dir = ""
        self.last_output_dir = ""
        self.loaded_pdf_path = None
        self.loaded_docx_path = None
        self.loaded_excel_path = None
        
        # Services
        self.excel_service = ExcelService()
        self.variable_service = VariableService()
        self.docx_variable_service = DocxVariableService()
        self.current_columns = []
        
        # Core Architecture components
        self.undo_stack = QUndoStack(self)
        self.undo_stack.indexChanged.connect(self._on_undo_stack_changed)
        
        self.preview_scene = PreviewScene()
        self.preview_scene.undo_stack = self.undo_stack
        self.preview_scene.set_default_text_style(font_family="Times New Roman", font_size=14, bold=False, italic=False)
        
        self.preview_controller = PreviewController(self.preview_scene)
        self.preview_controller.preview_updated.connect(self._on_preview_updated)
        
        QTimer.singleShot(100, self._show_welcome_screen)

        self._setup_ui()
        
        # Final wiring
        self.preview_scene.selection_changed.connect(self._on_selection_changed)
        self.preview_scene.scene_texts_changed.connect(self._on_scene_changed)

    def _show_welcome_screen(self):
        from app.ui.components.welcome_dialog import WelcomeDialog
        WelcomeDialog.show_if_needed(self)
        
    def _setup_ui(self):
        central_widget = QFrame()
        central_widget.setObjectName("mainWindowFrame")
        central_widget.setFrameShape(QFrame.Shape.NoFrame)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        from app.ui.components.title_bar import TitleBar
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)
        
        # Dedicated separator below menu bar
        menu_separator = QFrame()
        menu_separator.setFrameShape(QFrame.Shape.HLine)
        menu_separator.setFrameShadow(QFrame.Shadow.Plain)
        menu_separator.setFixedHeight(1)
        menu_separator.setStyleSheet("background-color: #3E3E42; border: none; color: #3E3E42;")
        main_layout.addWidget(menu_separator)
        
        self._setup_menu_bar()
        
        self.top_nav = TopNav()
        self.top_nav.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.top_nav.mode_changed.connect(self._switch_mode)
        main_layout.addWidget(self.top_nav)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        
        self.left_panel = self._create_left_panel()
        self.splitter.addWidget(self.left_panel)
        
        self.center_panel = self._create_center_panel()
        self.splitter.addWidget(self.center_panel)
        
        self.right_panel = self._create_right_panel()
        self.splitter.addWidget(self.right_panel)
        
        self.splitter.setSizes([280, 840, 280])
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setStretchFactor(2, 0)
        
        main_layout.addWidget(self.splitter, 1)

        self.status_bar = self._create_status_bar()
        main_layout.addWidget(self.status_bar)
        
        self.update_mode_ui(0)
        
    def _setup_menu_bar(self):
        menubar = self.title_bar.menu_bar
        
        # File Menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(lambda: self._new_project(prompt=True))
        file_menu.addAction(new_action)
        
        open_action = QAction("Open Template", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_project)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("Save Project", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_project)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save Project As", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self._save_project_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu
        self.edit_menu = menubar.addMenu("Edit")
        
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self._undo)
        self.edit_menu.addAction(self.undo_action)
        
        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.triggered.connect(self._redo)
        self.edit_menu.addAction(self.redo_action)
        
        self.edit_menu.addSeparator()
        
        self.delete_layer_action = QAction("Delete Selected Layer", self)
        self.delete_layer_action.setShortcut("Del")
        self.delete_layer_action.triggered.connect(self._delete_selected_layer)
        self.edit_menu.addAction(self.delete_layer_action)
        
        self.select_all_action = QAction("Select All Layers", self)
        self.select_all_action.setShortcut("Ctrl+A")
        self.select_all_action.triggered.connect(self._select_all_layers)
        self.edit_menu.addAction(self.select_all_action)
        
        # View Menu
        view_menu = menubar.addMenu("View")
        
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self._zoom_in_global)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self._zoom_out_global)
        view_menu.addAction(zoom_out_action)
        
        fit_page_action = QAction("Fit Page", self)
        fit_page_action.setShortcut("Ctrl+0")
        fit_page_action.triggered.connect(self._fit_page_global)
        view_menu.addAction(fit_page_action)
        
        # Help Menu
        help_menu = menubar.addMenu("Help")
        
        user_guide_action = QAction("User Guide", self)
        user_guide_action.setShortcut("F1")
        user_guide_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://docforge.thirumaldhakshna.in/docx-guide")))
        help_menu.addAction(user_guide_action)
        
        shortcuts_action = QAction("Keyboard Shortcuts", self)
        from app.ui.components.shortcuts_dialog import ShortcutsDialog
        shortcuts_action.triggered.connect(lambda: ShortcutsDialog(self).exec())
        help_menu.addAction(shortcuts_action)
        
        updates_action = QAction("Check for Updates", self)
        updates_action.triggered.connect(lambda: CustomDialog.information(self, "Updates", "You are running the latest version of DocForge."))
        help_menu.addAction(updates_action)
        
        website_action = QAction("Visit Website", self)
        website_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://docforge.thirumaldhakshna.in")))
        help_menu.addAction(website_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("About DocForge", self)
        from app.utils.path_helpers import resource_path
        icon_path = resource_path("assets/icons/app_64.png").replace('\\', '/')
        
        about_text = (
            "<div align='center'>"
            f"<img src='{icon_path}' width='64' height='64'><br><br>"
            "<b>DocForge</b><br><br>"
            "Advanced PDF & DOCX Template Automation Platform<br><br>"
            "Generate personalized PDF and DOCX documents<br>"
            "from templates using spreadsheet data.<br><br>"
            "Author:<br>"
            "Thirumal Dhakshnamoorthy<br><br>"
            "Copyright © 2026<br>"
            "Thirumal Dhakshnamoorthy<br>"
            "All Rights Reserved.<br><br>"
            "<i>Forge Documents. Automate Work.</i>"
            "</div>"
        )
        about_action.triggered.connect(lambda: CustomDialog.about(self, "About DocForge", about_text))
        help_menu.addAction(about_action)

    def set_dirty(self, dirty=True):
        self.is_dirty = dirty
        title = "DocForge"
        if self.current_project_path:
            title += f" - {os.path.basename(self.current_project_path)}"
        if self.is_dirty:
            title += " *"
        self.setWindowTitle(title)
        if hasattr(self, 'top_nav'):
            self.top_nav.set_title(title)

    def _create_status_bar(self):
        bar = QWidget()
        bar.setObjectName("statusBarWidget")
        bar.setFixedHeight(24)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(0)

        self.status_label = QLabel("Ready | PDF Designer | Zoom 100%")
        self.status_label.setObjectName("statusBarLabel")
        layout.addWidget(self.status_label)
        layout.addStretch()

        return bar

    def _update_status_bar(self):
        if not hasattr(self, 'status_label'):
            return

        is_docx_mode = self.stacked_widget.currentIndex() == 0
        mode = "DOCX Mode" if is_docx_mode else "PDF Designer"
        canvas = self.docx_canvas if is_docx_mode else self.pdf_canvas
        zoom = int(round(canvas.view.get_zoom() * 100))
        self.status_label.setText(f"Ready | {mode} | Zoom {zoom}%")

    def _on_scene_changed(self):
        self.set_dirty(True)
        self._validate_variables()

    def _on_selection_changed(self, layer):
        self.typography_card.update_from_layer(layer)
        if layer:
            font = layer.font()
            self.preview_scene.set_default_text_style(
                font_family=font.family(),
                font_size=font.pointSize(),
                bold=font.bold(),
                italic=font.italic()
            )

    def update_mode_ui(self, index):
        is_docx_mode = index == 0
        self.stacked_widget.setCurrentIndex(index)
        
        if hasattr(self, 'typography_card'):
            self.typography_card.setVisible(not is_docx_mode)
            
        if hasattr(self, 'export_settings_card'):
            self.export_settings_card.set_mode(is_docx_mode)
            
        if hasattr(self, 'edit_menu'):
            self.undo_action.setEnabled(not is_docx_mode and self.undo_stack.canUndo())
            self.redo_action.setEnabled(not is_docx_mode and self.undo_stack.canRedo())
            self.delete_layer_action.setEnabled(not is_docx_mode)

        self._update_status_bar()

    def _on_undo_stack_changed(self, index):
        self.set_dirty(True)
        self.update_mode_ui(self.stacked_widget.currentIndex())

    def _undo(self):
        from PyQt6.QtWidgets import QLineEdit, QTextEdit, QPlainTextEdit
        fw = QApplication.focusWidget()
        if isinstance(fw, (QLineEdit, QTextEdit, QPlainTextEdit)):
            return
            
        if self.stacked_widget.currentIndex() != 0 and self.undo_stack.canUndo():
            self.undo_stack.undo()

    def _redo(self):
        from PyQt6.QtWidgets import QLineEdit, QTextEdit, QPlainTextEdit
        fw = QApplication.focusWidget()
        if isinstance(fw, (QLineEdit, QTextEdit, QPlainTextEdit)):
            return
            
        if self.stacked_widget.currentIndex() != 0 and self.undo_stack.canRedo():
            self.undo_stack.redo()

    def _delete_selected_layer(self):
        from PyQt6.QtWidgets import QLineEdit, QTextEdit, QPlainTextEdit
        fw = QApplication.focusWidget()
        if isinstance(fw, (QLineEdit, QTextEdit, QPlainTextEdit)):
            return
            
        if self.stacked_widget.currentIndex() == 0:
            return
            
        layer = self.preview_scene.get_active_layer()
        if layer:
            cmd = DeleteLayerCommand(self.preview_scene, layer)
            self.undo_stack.push(cmd)

    def _select_all_layers(self):
        from PyQt6.QtWidgets import QLineEdit, QTextEdit, QPlainTextEdit
        fw = QApplication.focusWidget()
        if isinstance(fw, (QLineEdit, QTextEdit, QPlainTextEdit)):
            return
            
        if self.stacked_widget.currentIndex() == 0:
            return
            
        for item in self.preview_scene.items():
            if isinstance(item, TextLayerItem):
                item.setSelected(True)

    def _zoom_in_global(self):
        if self.stacked_widget.currentIndex() == 0:
            self.docx_canvas.view.zoom_in()
        else:
            self.pdf_canvas.view.zoom_in()

    def _zoom_out_global(self):
        if self.stacked_widget.currentIndex() == 0:
            self.docx_canvas.view.zoom_out()
        else:
            self.pdf_canvas.view.zoom_out()

    def _fit_page_global(self):
        if self.stacked_widget.currentIndex() == 0:
            self.docx_canvas.view.fit_to_scene()
        else:
            self.pdf_canvas.view.fit_to_scene()

    def _switch_mode(self, index):
        self.update_mode_ui(index)
        self.set_dirty(True)
        self._validate_variables()

    def _create_left_panel(self):
        panel = QWidget()
        panel.setObjectName("leftPanelContainer")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.upload_card = UploadCard()
        self.upload_card.template_uploaded.connect(self._on_template_uploaded)
        self.upload_card.excel_uploaded.connect(self._on_excel_uploaded)
        layout.addWidget(self.upload_card)
        
        self.fields_card = FieldsCard()
        self.fields_card.field_clicked.connect(self._on_field_clicked)
        layout.addWidget(self.fields_card)
        
        layout.addStretch()
        
        return panel

    def _create_center_panel(self):
        panel = QWidget()
        panel.setObjectName("centerPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.stacked_widget = QStackedWidget()
        
        self.docx_canvas = PreviewCanvas("DOCX Mode", self.preview_scene)
        self.pdf_canvas = PreviewCanvas("PDF Designer Mode", self.preview_scene)
        self.docx_canvas.view.zoom_changed.connect(self._update_status_bar)
        self.pdf_canvas.view.zoom_changed.connect(self._update_status_bar)
        
        self.stacked_widget.addWidget(self.docx_canvas)
        self.stacked_widget.addWidget(self.pdf_canvas)
        
        layout.addWidget(self.stacked_widget)
        return panel

    def _create_right_panel(self):
        panel = QWidget()
        panel.setObjectName("rightPanelContainer")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.typography_card = TypographyCard()
        self.typography_card.setEnabled(False) 
        self.typography_card.font_changed.connect(self._on_font_changed)
        self.typography_card.size_changed.connect(self._on_size_changed)
        self.typography_card.bold_toggled.connect(self._on_bold_toggled)
        self.typography_card.italic_toggled.connect(self._on_italic_toggled)
        self.typography_card.color_changed.connect(self._on_color_changed)
        layout.addWidget(self.typography_card)

        divider = QFrame()
        divider.setObjectName("rightSectionDivider")
        divider.setFrameShape(QFrame.Shape.NoFrame)
        layout.addWidget(divider)
        
        self.export_settings_card = ExportSettingsCard()
        layout.addWidget(self.export_settings_card)
        layout.addStretch()
        
        self.actions_card = ActionsCard()
        self.actions_card.generate_clicked.connect(self._on_generate_clicked)
        layout.addWidget(self.actions_card)
        
        return panel

    def _on_template_uploaded(self, filepath):
        self.set_dirty(True)
        _, ext = os.path.splitext(filepath.lower())
        if ext == '.pdf':
            self.loaded_pdf_path = filepath
        elif ext == '.docx':
            self.loaded_docx_path = filepath
            try:
                vars = self.docx_variable_service.extract_variables(filepath)
                self.fields_card.set_used_variables(vars)
                if self.current_columns:
                    missing = [v for v in vars if v not in self.current_columns]
                    self.fields_card.show_warning(missing)
            except Exception as e:
                print(f"Failed to extract DOCX variables: {e}")
        self.preview_controller.load_file(filepath)
        
    def _on_preview_updated(self, has_preview, message):
        if has_preview:
            self.docx_canvas.show_preview()
            self.pdf_canvas.show_preview()
        else:
            if message:
                self.docx_canvas.show_message(message)
                self.pdf_canvas.show_message(message)
            else:
                self.docx_canvas.show_message("Import a PDF or DOCX template to begin editing")
                self.pdf_canvas.show_message("Import a PDF or DOCX template to begin editing")

    def _on_excel_uploaded(self, filepath):
        try:
            self.current_columns = self.excel_service.get_columns(filepath)
            self.loaded_excel_path = filepath
            self.fields_card.set_columns(self.current_columns)
            self.set_dirty(True)
            self._validate_variables()
        except Exception as e:
            CustomDialog.warning(self, "Error", f"Failed to load Excel: {e}")

    def _validate_variables(self):
        is_docx_mode = self.stacked_widget.currentIndex() == 0
        if is_docx_mode:
            if not self.loaded_docx_path:
                self.fields_card.set_used_variables([])
                self.fields_card.show_warning([])
                return
            try:
                vars = self.docx_variable_service.extract_variables(self.loaded_docx_path)
                self.fields_card.set_used_variables(vars)
                if self.current_columns:
                    missing = [v for v in vars if v not in self.current_columns]
                    self.fields_card.show_warning(missing)
                else:
                    self.fields_card.show_warning([])
            except:
                pass
        else:
            texts = [i.toPlainText() for i in self.preview_scene.items() if isinstance(i, TextLayerItem)]
            all_vars = set()
            for t in texts:
                all_vars.update(self.variable_service.extract_variables(t))
                
            self.fields_card.set_used_variables(sorted(list(all_vars)))
            
            if self.current_columns:
                missing = self.variable_service.find_missing_variables(texts, self.current_columns)
                self.fields_card.show_warning(missing)
            else:
                self.fields_card.show_warning([])

    def _on_field_clicked(self, field_name):
        if self.stacked_widget.currentIndex() == 0:
            CustomDialog.information(self, "DOCX Mode", "In DOCX Mode, please insert variables directly into your Word document before uploading.")
            return
            
        layer = self.preview_scene.get_active_layer()
        placeholder = f"{{{{{field_name}}}}}"
        if layer:
            from app.editor.commands import TextChangeCommand
            current = layer.toPlainText()
            new_text = current + " " + placeholder if current else placeholder
            cmd = TextChangeCommand(layer, current, new_text)
            self.undo_stack.push(cmd)
        else:
            if not self.preview_scene.page_item:
                return
            item = self.preview_scene.create_text_layer_item(placeholder)
            cmd = AddLayerCommand(self.preview_scene, item, center=True)
            self.undo_stack.push(cmd)

    def _on_font_changed(self, family):
        self.preview_scene.set_default_text_style(font_family=family)
        layer = self.preview_scene.get_active_layer()
        if layer:
            old_family = layer.font().family()
            if old_family != family:
                cmd = PropertyChangeCommand(layer, 'font_family', old_family, family)
                self.undo_stack.push(cmd)

    def _on_size_changed(self, size):
        self.preview_scene.set_default_text_style(font_size=size)
        layer = self.preview_scene.get_active_layer()
        if layer:
            old_size = layer.font().pointSize()
            if old_size != size:
                cmd = PropertyChangeCommand(layer, 'font_size', old_size, size)
                self.undo_stack.push(cmd)

    def _on_bold_toggled(self, checked):
        self.preview_scene.set_default_text_style(bold=checked)
        layer = self.preview_scene.get_active_layer()
        if layer:
            old_bold = layer.font().bold()
            if old_bold != checked:
                cmd = PropertyChangeCommand(layer, 'bold', old_bold, checked)
                self.undo_stack.push(cmd)

    def _on_italic_toggled(self, checked):
        self.preview_scene.set_default_text_style(italic=checked)
        layer = self.preview_scene.get_active_layer()
        if layer:
            old_italic = layer.font().italic()
            if old_italic != checked:
                cmd = PropertyChangeCommand(layer, 'italic', old_italic, checked)
                self.undo_stack.push(cmd)

    def _on_color_changed(self, color):
        layer = self.preview_scene.get_active_layer()
        if layer:
            old_color = layer.defaultTextColor()
            if old_color != color:
                cmd = PropertyChangeCommand(layer, 'color', old_color, color)
                self.undo_stack.push(cmd)

    # --- Export Engine ---

    def _on_generate_clicked(self):
        is_docx_mode = self.stacked_widget.currentIndex() == 0
        
        if is_docx_mode:
            if not self.loaded_docx_path:
                CustomDialog.export_failed(self, "No DOCX template is loaded.")
                return
            try:
                vars = self.docx_variable_service.extract_variables(self.loaded_docx_path)
                missing = [v for v in vars if v not in self.current_columns] if self.current_columns else []
            except Exception as e:
                CustomDialog.export_failed(self, f"Could not read variables from the DOCX template.\n\n{e}")
                return
        else:
            if not self.loaded_pdf_path:
                CustomDialog.export_failed(self, "No PDF template is loaded.")
                return
            texts = [i.toPlainText() for i in self.preview_scene.items() if isinstance(i, TextLayerItem)]
            if not texts:
                CustomDialog.export_failed(self, "No dynamic text layers have been added to the template.")
                return
            missing = self.variable_service.find_missing_variables(texts, self.current_columns)
            
        if not self.loaded_excel_path or not self.current_columns:
            CustomDialog.export_failed(self, "No data source is loaded.")
            return
            
        if missing:
            CustomDialog.export_failed(self, f"Missing fields in the data source:\n{', '.join(missing)}")
            return
            
        start_dir = self.last_output_dir
        if not start_dir or not os.path.exists(start_dir):
            start_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
            
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory", start_dir)
        if not output_dir:
            return
            
        self.last_output_dir = output_dir
            
        export_type = self.export_settings_card.get_export_type()
        output_format = self.export_settings_card.get_output_format()
        
        mode_str = "DOCX" if is_docx_mode else "PDF Designer"
        import logging
        logging.info(f"--- Export Diagnostics ---")
        logging.info(f"Mode: {mode_str}")
        logging.info(f"Export Type: {export_type}")
        logging.info(f"Output Format: {output_format}")
        
        template_path = self.loaded_docx_path if is_docx_mode else self.loaded_pdf_path
        logging.info(f"Template Path: {template_path}")
        logging.info(f"Excel Path: {self.loaded_excel_path}")
        
        print(f"--- Export Diagnostics ---\nMode: {mode_str}\nExport Type: {export_type}\nOutput Format: {output_format}\nTemplate Path: {template_path}\nExcel Path: {self.loaded_excel_path}\n")

        stage_label = "Generating PDF" if output_format == "pdf" else "Generating document"
        progress_dialog = ExportProgressDialog(self, stage_label=stage_label)
        progress_dialog.show_centered()
        progress_dialog.set_progress(5, 100)
        QApplication.processEvents()

        try:
            excel_rows = self.excel_service.load_excel(self.loaded_excel_path)
        except Exception as e:
            progress_dialog.close()
            CustomDialog.export_failed(self, f"Could not load the data source.\n\n{e}")
            return
            
        if not excel_rows:
            progress_dialog.close()
            CustomDialog.export_failed(self, "The selected data source is empty.")
            return

        progress_dialog.set_progress(20, 100)
        QApplication.processEvents()
        
        def progress_update(current, total):
            export_percent = int(round((current / max(total, 1)) * 65))
            progress_dialog.set_progress(25 + export_percent, 100)
            QApplication.processEvents()

        saved_to = None
        export_cancelled = False

        try:
            if is_docx_mode:
                from app.export.docx_exporter import DocxExporter
                exporter = DocxExporter()
                if export_type == "combined":
                    exported_path = exporter.export_combined_docx(self.loaded_docx_path, excel_rows, output_dir, output_format=output_format, progress_callback=progress_update)
                    if output_format == "pdf":
                        assert str(exported_path).lower().endswith(".pdf"), f"Validation Failed: Expected .pdf output, generated {exported_path}"
                    elif output_format == "docx":
                        assert str(exported_path).lower().endswith(".docx"), f"Validation Failed: Expected .docx output, generated {exported_path}"
                    saved_to = exported_path or output_dir
                else:
                    exported_paths = exporter.export_bulk_docx(self.loaded_docx_path, excel_rows, output_dir, output_format=output_format, progress_callback=progress_update)
                    for p in exported_paths:
                        if output_format == "pdf":
                            assert str(p).lower().endswith(".pdf"), f"Validation Failed: Expected .pdf output, generated {p}"
                        elif output_format == "docx":
                            assert str(p).lower().endswith(".docx"), f"Validation Failed: Expected .docx output, generated {p}"
                    saved_to = output_dir
            else:
                layers = [item.to_dict() for item in self.preview_scene.items() if isinstance(item, TextLayerItem)]
                ui_rect = self.preview_scene.page_item.boundingRect()
                
                import logging
                var_count = sum(1 for layer in layers if '{' in layer.get('text', '') or '$' in layer.get('text', ''))
                logging.info(f"Designer items count: {len(self.preview_scene.items())}")
                logging.info(f"Variable items count: {var_count}")
                logging.info(f"Text items count: {len(layers)}")
                
                from app.export.export_worker import ExportWorker
                worker = ExportWorker(self.loaded_pdf_path, layers, excel_rows, output_dir, ui_rect, export_type=export_type)
                
                exported_path = worker.run(progress_callback=progress_update)
                if not worker.is_cancelled:
                    saved_to = exported_path if export_type == "combined" and exported_path else output_dir
                else:
                    export_cancelled = True

            progress_dialog.set_progress(100, 100)
            QApplication.processEvents()
        except Exception as e:
            progress_dialog.close()
            CustomDialog.export_failed(self, str(e))
            return
        finally:
            progress_dialog.close()

        if export_cancelled:
            CustomDialog.information(self, "Export Cancelled", "Bulk export was cancelled safely.")
        else:
            from app.ui.components.export_success_dialog import ExportSuccessDialog
            doc_count = len(excel_rows) if excel_rows else 0
            export_mode_str = "Combined Document" if export_type == "combined" else "Separate Documents"
            fmt = "PDF" if not is_docx_mode else ("DOCX" if output_format == "docx" else "PDF")
            
            dlg = ExportSuccessDialog(
                self, 
                saved_to or output_dir, 
                doc_count, 
                fmt, 
                export_mode_str
            )
            dlg.exec()
            
    # --- Project Management ---
    
    def _prompt_save_if_dirty(self):
        if not self.is_dirty:
            return True
            
        reply = CustomDialog.question(
            self, 'Unsaved Changes',
            'You have unsaved changes. Do you want to save before continuing?',
            CustomDialog.Save | CustomDialog.Discard | CustomDialog.Cancel,
            CustomDialog.Save
        )
        
        if reply == CustomDialog.Save:
            return self._save_project()
        elif reply == CustomDialog.Cancel:
            return False
            
        return True

    def _new_project(self, prompt=True):
        if prompt and not self._prompt_save_if_dirty():
            return
            
        self.current_project_path = None
        self.loaded_pdf_path = None
        self.loaded_docx_path = None
        self.loaded_excel_path = None
        self.current_columns = []
        
        self.preview_scene.clear()
        self.preview_scene.page_item = None
        self.preview_scene.helper_item = None
        self._on_preview_updated(False, "")
        
        self.fields_card.set_columns([])
        self.fields_card.set_used_variables([])
        self.fields_card.show_warning([])
        
        self.docx_canvas.view.set_zoom(1.0)
        self.pdf_canvas.view.set_zoom(1.0)
        
        self.set_dirty(False)

    def _save_project(self):
        if not self.current_project_path:
            return self._save_project_as()
        return self._do_save(self.current_project_path)
        
    def _get_project_start_dir(self):
        start_dir = self.last_project_dir
        if not start_dir or not os.path.exists(start_dir):
            start_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        return start_dir

    def _save_project_as(self):
        start_dir = self._get_project_start_dir()
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Project As", start_dir, "DocForge Template (*.brtemplate)"
        )
        if not path:
            return False
            
        self.last_project_dir = os.path.dirname(path)
        return self._do_save(path)
        
    def _do_save(self, path):
        layers = []
        for item in self.preview_scene.items():
            if isinstance(item, TextLayerItem):
                layers.append(item.to_dict())
                
        zoom = self.docx_canvas.view.get_zoom() if self.stacked_widget.currentIndex() == 0 else self.pdf_canvas.view.get_zoom()
        
        data = {
            'mode': self.stacked_widget.currentIndex(),
            'pdf_path': self.loaded_pdf_path,
            'docx_path': self.loaded_docx_path,
            'excel_path': self.loaded_excel_path,
            'zoom': zoom,
            'layers': layers
        }
        
        try:
            ProjectService.save_project(path, data)
            self.current_project_path = path
            self.set_dirty(False)
            return True
        except Exception as e:
            CustomDialog.critical(self, "Error", f"Failed to save project: {str(e)}")
            return False

    def _open_project(self):
        if not self._prompt_save_if_dirty():
            return
            
        start_dir = self._get_project_start_dir()
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", start_dir, "DocForge Template (*.brtemplate)"
        )
        if not path:
            return
            
        self.last_project_dir = os.path.dirname(path)
            
        try:
            data = ProjectService.load_project(path)
            self._apply_project_data(data, path)
        except Exception as e:
            CustomDialog.critical(self, "Error", f"Failed to load project: {str(e)}")
            
    def _apply_project_data(self, data, path):
        self._new_project(prompt=False)
        
        # Restore Mode
        mode = data.get('mode', 0)
        if mode == 0:
            self.top_nav.btn_docx.setChecked(True)
        else:
            self.top_nav.btn_pdf.setChecked(True)
        self._switch_mode(mode)
        
        # Restore Excel
        excel_path = data.get('excel_path')
        if excel_path and os.path.exists(excel_path):
            self._on_excel_uploaded(excel_path)
            
        # Restore Canvas state
        pdf_path = data.get('pdf_path')
        if pdf_path and os.path.exists(pdf_path):
            self._on_template_uploaded(pdf_path)
            
        docx_path = data.get('docx_path')
        if docx_path and os.path.exists(docx_path):
            self.loaded_docx_path = docx_path
            
        # Reconstruct Layers
        first_layer = None
        for layer_data in data.get('layers', []):
            if layer_data.get('type') == 'text':
                item = TextLayerItem.from_dict(layer_data)
                self.preview_scene.addItem(item)
                if not first_layer:
                    first_layer = item
                    
        if first_layer:
            first_layer.setSelected(True)
                
        # Restore Zoom
        zoom = data.get('zoom', 1.0)
        self.docx_canvas.view.set_zoom(zoom)
        self.pdf_canvas.view.set_zoom(zoom)
        
        # Trigger UI refresh
        self.preview_scene._update_empty_helper()
        self._validate_variables()
        
        self.current_project_path = path
        self.set_dirty(False)

    def closeEvent(self, event):
        if not self._prompt_save_if_dirty():
            event.ignore()
        else:
            event.accept()
