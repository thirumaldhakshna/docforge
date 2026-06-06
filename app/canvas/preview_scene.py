from PyQt6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QGraphicsDropShadowEffect, QGraphicsTextItem
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import pyqtSignal, Qt
from app.editor.items.text_layer_item import TextLayerItem

class PreviewScene(QGraphicsScene):
    selection_changed = pyqtSignal(object)
    scene_texts_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.page_item = None
        self.helper_item = None
        self.default_font_family = "Times New Roman"
        self.default_font_size = 14
        self.default_bold = False
        self.default_italic = False
        self.current_tool = "hand"
        self.setBackgroundBrush(QColor("#1E1E1E"))
        self.selectionChanged.connect(self._on_selection_changed)

    def set_tool(self, tool):
        self.current_tool = tool

    def set_default_text_style(self, font_family=None, font_size=None, bold=None, italic=None):
        if font_family is not None:
            self.default_font_family = font_family
        if font_size is not None:
            self.default_font_size = font_size
        if bold is not None:
            self.default_bold = bold
        if italic is not None:
            self.default_italic = italic

    def create_text_layer_item(self, text="Text"):
        return TextLayerItem(
            text,
            font_family=self.default_font_family,
            font_size=self.default_font_size,
            bold=self.default_bold,
            italic=self.default_italic
        )

    def set_preview_pixmap(self, pixmap):
        self.clear()
        self.page_item = None
        self.helper_item = None
        
        if pixmap:
            self.page_item = QGraphicsPixmapItem(pixmap)
            
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(32)
            shadow.setColor(QColor(0, 0, 0, 110))
            shadow.setOffset(0, 8)
            self.page_item.setGraphicsEffect(shadow)
            
            self.page_item.setZValue(-1)
            self.addItem(self.page_item)
            self.setSceneRect(self.page_item.boundingRect().adjusted(-56, -56, 56, 56))
            
            self._update_empty_helper()
        else:
            self.setSceneRect(0, 0, 0, 0)
            
    def add_text_layer(self, text="Text", center=True):
        if not self.page_item:
            return None
            
        item = self.create_text_layer_item(text)
        self.addItem(item)
        
        if center:
            rect = self.page_item.boundingRect()
            item_rect = item.boundingRect()
            x = rect.width() / 2 - item_rect.width() / 2
            y = rect.height() / 2 - item_rect.height() / 2
            item.setPos(x, y)
            
        self.clearSelection()
        item.setSelected(True)
        self._update_empty_helper()
        self.scene_texts_changed.emit()
        return item

    def removeItem(self, item):
        super().removeItem(item)
        if isinstance(item, TextLayerItem):
            self._update_empty_helper()
            self.scene_texts_changed.emit()

    def get_active_layer(self):
        items = self.selectedItems()
        if items and isinstance(items[0], TextLayerItem):
            return items[0]
        return None

    def _on_selection_changed(self):
        self.selection_changed.emit(self.get_active_layer())

    def _on_item_text_changed(self, item):
        self.scene_texts_changed.emit()
        
    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos(), self.views()[0].transform() if self.views() else None)
        if item is None or item == self.page_item:
            self.clearSelection()
        super().mousePressEvent(event)

    def _update_empty_helper(self):
        if not self.page_item:
            return
            
        text_layers = [i for i in self.items() if isinstance(i, TextLayerItem)]
        
        if len(text_layers) == 0:
            if not self.helper_item:
                self.helper_item = QGraphicsTextItem("Use the Text tool to add dynamic fields")
                self.helper_item.setDefaultTextColor(QColor("#94A3B8"))
                font = QFont("Inter", 12, QFont.Weight.Bold)
                self.helper_item.setFont(font)
                self.addItem(self.helper_item)
                
                rect = self.page_item.boundingRect()
                self.helper_item.setPos(rect.width() - self.helper_item.boundingRect().width() - 20, 20)
            self.helper_item.show()
        else:
            if self.helper_item:
                self.helper_item.hide()
