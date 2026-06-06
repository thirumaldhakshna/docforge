from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class LayersCard(QWidget):
    def __init__(self):
        super().__init__()
        self.setProperty("class", "CardWidget")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 16)
        
        title = QLabel("Layers")
        title.setProperty("class", "CardTitle")
        layout.addWidget(title)
        
        empty_label = QLabel("No layers yet")
        empty_label.setProperty("class", "emptyState")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(empty_label)
        
        layout.addStretch()
