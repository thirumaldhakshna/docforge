from PyQt6.QtWidgets import QGraphicsTextItem, QGraphicsItem
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt

class TextLayerItem(QGraphicsTextItem):
    def __init__(self, text="Text", parent=None, font_family="Times New Roman", font_size=14, bold=False, italic=False):
        super().__init__(text, parent)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsFocusable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        
        font = QFont(font_family, font_size)
        font.setBold(bold)
        font.setItalic(italic)
        self.setFont(font)
        
        self.is_editing = False
        
        self.document().contentsChanged.connect(self._on_contents_changed)

    def _on_contents_changed(self):
        if self.scene() and hasattr(self.scene(), '_on_item_text_changed'):
            self.scene()._on_item_text_changed(self)

    def paint(self, painter: QPainter, option, widget):
        super().paint(painter, option, widget)
        
        if self.isSelected() and not self.is_editing:
            rect = self.boundingRect()
            pen = QPen(QColor("#2563EB"))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            
            rect.adjust(1, 1, -1, -1)
            painter.drawRoundedRect(rect, 4, 4)

    def mouseDoubleClickEvent(self, event):
        if self.textInteractionFlags() == Qt.TextInteractionFlag.NoTextInteraction:
            self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
            self.setFocus()
            self.is_editing = True
            self._undo_old_text = self.toPlainText()
            self.update()
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        self._undo_start_pos = self.pos()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if hasattr(self, '_undo_start_pos') and self.pos() != self._undo_start_pos:
            scene = self.scene()
            if scene and hasattr(scene, 'undo_stack'):
                from app.editor.commands import MoveLayerCommand
                cmd = MoveLayerCommand(self, self._undo_start_pos, self.pos())
                scene.undo_stack.push(cmd)

    def focusOutEvent(self, event):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.is_editing = False
        
        if self.toPlainText().strip() == "":
            scene = self.scene()
            if scene:
                if hasattr(scene, 'undo_stack'):
                    from app.editor.commands import DeleteLayerCommand
                    cmd = DeleteLayerCommand(scene, self)
                    scene.undo_stack.push(cmd)
                else:
                    scene.removeItem(self)
                return
        else:
            if hasattr(self, '_undo_old_text') and self.toPlainText() != self._undo_old_text:
                scene = self.scene()
                if scene and hasattr(scene, 'undo_stack'):
                    from app.editor.commands import TextChangeCommand
                    cmd = TextChangeCommand(self, self._undo_old_text, self.toPlainText())
                    scene.undo_stack.push(cmd)
                
        self.update()
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        if self.is_editing:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Escape):
                self.clearFocus()
                return
        super().keyPressEvent(event)

    def to_dict(self):
        font = self.font()
        color = self.defaultTextColor().name()
        rect = self.boundingRect()
        return {
            'type': 'text',
            'text': self.toPlainText(),
            'x': self.pos().x(),
            'y': self.pos().y(),
            'width': rect.width(),
            'height': rect.height(),
            'font_family': font.family(),
            'font_size': font.pointSize(),
            'color': color,
            'bold': font.bold(),
            'italic': font.italic(),
            'page_number': 0
        }

    @classmethod
    def from_dict(cls, data):
        item = cls(data.get('text', 'Text'))
        item.setPos(data.get('x', 0), data.get('y', 0))
        
        font = QFont(data.get('font_family', 'Times New Roman'), data.get('font_size', 14))
        font.setBold(data.get('bold', False))
        font.setItalic(data.get('italic', False))
        item.setFont(font)
        
        color = data.get('color', '#1E293B')
        item.setDefaultTextColor(QColor(color))
        
        return item
