from PyQt6.QtWidgets import QGraphicsView, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QPainter, QWheelEvent, QMouseEvent
from app.editor.items.text_layer_item import TextLayerItem

class PDFCanvasView(QGraphicsView):
    zoom_changed = pyqtSignal(float)
    
    def __init__(self, scene=None):
        super().__init__(scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # We rely on CSS / Scene background
        self.setStyleSheet("background: transparent; border: none;")
        
        self._zoom = 1.0
        self._is_panning = False
        self._last_pan_point = QPoint()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        item = self.itemAt(event.position().toPoint())
        scene = self.scene()
        scene_pos = self.mapToScene(event.position().toPoint())
        clicked_layer = isinstance(item, TextLayerItem)

        if clicked_layer:
            super().mousePressEvent(event)
            return

        if getattr(scene, 'current_tool', 'hand') == 'text' and getattr(scene, 'page_item', None):
            if scene.page_item.contains(scene.page_item.mapFromScene(scene_pos)):
                item = scene.create_text_layer_item("Text")
                item.setPos(scene_pos)
                from app.editor.commands import AddLayerCommand
                if hasattr(scene, 'undo_stack'):
                    scene.undo_stack.push(AddLayerCommand(scene, item, center=False))
                else:
                    scene.addItem(item)
                    scene.clearSelection()
                    item.setSelected(True)
                    scene._update_empty_helper()
                    scene.scene_texts_changed.emit()
                event.accept()
                return

        if getattr(scene, 'current_tool', 'hand') == 'hand':
            self._is_panning = True
            self._last_pan_point = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_panning:
            delta = event.position().toPoint() - self._last_pan_point
            self._last_pan_point = event.position().toPoint()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self._is_panning:
            self._is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return

        super().mouseReleaseEvent(event)
        
    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)
            
    def zoom_in(self):
        self._set_zoom(self._zoom * 1.1)
        
    def zoom_out(self):
        self._set_zoom(self._zoom / 1.1)
        
    def set_zoom(self, zoom_factor):
        self._set_zoom(zoom_factor)
        
    def _set_zoom(self, new_zoom):
        # clamp zoom
        new_zoom = max(0.1, min(new_zoom, 5.0))
        if new_zoom != self._zoom:
            self._zoom = new_zoom
            # reset transform
            self.resetTransform()
            self.scale(self._zoom, self._zoom)
            self.zoom_changed.emit(self._zoom)
            
    def get_zoom(self):
        return self._zoom

    def fit_to_scene(self):
        if self.scene():
            rect = self.scene().sceneRect()
            if rect.width() > 0 and rect.height() > 0:
                self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
                self._zoom = self.transform().m11()
                self.zoom_changed.emit(self._zoom)
