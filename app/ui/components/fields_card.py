from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem
from PyQt6.QtCore import pyqtSignal, Qt

class FieldsCard(QWidget):
    field_clicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 0)
        layout.setSpacing(8)
        
        title = QLabel("DATA FIELDS")
        title.setProperty("class", "CardTitle")
        layout.addWidget(title)
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        
        # Missing Variable Warning Label
        self.warning_label = QLabel()
        self.warning_label.setStyleSheet("color: #F87171; font-weight: bold; background-color: #450A0A; padding: 8px; border-radius: 2px;")
        self.warning_label.setWordWrap(True)
        self.warning_label.hide()
        content_layout.addWidget(self.warning_label)
        
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search fields...")
        self.search_field.textChanged.connect(self._filter_fields)
        content_layout.addWidget(self.search_field)
        
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.setMinimumHeight(168)
        content_layout.addWidget(self.list_widget)
        
        # Used Variables Section
        used_title = QLabel("VARIABLES")
        used_title.setProperty("class", "CardTitle")
        used_title.setContentsMargins(0, 16, 0, 0)
        content_layout.addWidget(used_title)
        
        self.used_list = QListWidget()
        self.used_list.setMinimumHeight(96)
        self.used_list.setMaximumHeight(132)
        content_layout.addWidget(self.used_list)
        
        layout.addLayout(content_layout)
        
        self._all_columns = []
        self.set_used_variables([]) # Initialize empty

    def set_columns(self, columns):
        self._all_columns = columns
        self._populate_fields(columns)
        
    def _populate_fields(self, columns):
        self.list_widget.clear()
        for field in columns:
            item = QListWidgetItem(f"{{{field}}}")
            item.setData(Qt.ItemDataRole.UserRole, field)
            self.list_widget.addItem(item)
            
    def _filter_fields(self, text):
        filtered = [c for c in self._all_columns if text.lower() in c.lower()]
        self._populate_fields(filtered)
        
    def set_used_variables(self, variables):
        self.used_list.clear()
        if not variables:
            item = QListWidgetItem("No variables used")
            item.setForeground(Qt.GlobalColor.gray)
            self.used_list.addItem(item)
        else:
            for v in variables:
                item = QListWidgetItem(f"{{{v}}}")
                item.setData(Qt.ItemDataRole.UserRole, v)
                self.used_list.addItem(item)
                
    def show_warning(self, missing_vars):
        if missing_vars:
            self.warning_label.setText(f"Missing in Excel: {', '.join(missing_vars)}")
            self.warning_label.show()
        else:
            self.warning_label.hide()

    def _on_item_clicked(self, item):
        self.field_clicked.emit(item.data(Qt.ItemDataRole.UserRole) or item.text().strip("{}"))
