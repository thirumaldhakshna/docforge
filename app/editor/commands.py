from PyQt6.QtGui import QUndoCommand

class AddLayerCommand(QUndoCommand):
    def __init__(self, scene, item, center=True, description="Add Layer"):
        super().__init__(description)
        self.scene = scene
        self.item = item
        self.center = center
        self.is_first_redo = True
        
    def redo(self):
        if self.is_first_redo:
            self.is_first_redo = False
            # During the very first creation, we assume it's added manually by scene wrapper
            # or we do the adding here!
            # Let's just always do the adding here to make it safe.
            if self.item not in self.scene.items():
                self.scene.addItem(self.item)
                
            if self.center and self.scene.page_item:
                rect = self.scene.page_item.boundingRect()
                item_rect = self.item.boundingRect()
                x = rect.width() / 2 - item_rect.width() / 2
                y = rect.height() / 2 - item_rect.height() / 2
                self.item.setPos(x, y)
                
            self.scene.clearSelection()
            self.item.setSelected(True)
        else:
            if self.item not in self.scene.items():
                self.scene.addItem(self.item)
            self.scene.clearSelection()
            self.item.setSelected(True)
            
        self.scene._update_empty_helper()
        self.scene.scene_texts_changed.emit()
            
    def undo(self):
        if self.item in self.scene.items():
            self.scene.removeItem(self.item)
        self.scene._update_empty_helper()
        self.scene.scene_texts_changed.emit()

class DeleteLayerCommand(QUndoCommand):
    def __init__(self, scene, item, description="Delete Layer"):
        super().__init__(description)
        self.scene = scene
        self.item = item
        
    def redo(self):
        if self.item in self.scene.items():
            self.scene.removeItem(self.item)
        self.scene._update_empty_helper()
        self.scene.scene_texts_changed.emit()
        
    def undo(self):
        if self.item not in self.scene.items():
            self.scene.addItem(self.item)
        self.scene.clearSelection()
        self.item.setSelected(True)
        self.scene._update_empty_helper()
        self.scene.scene_texts_changed.emit()

class MoveLayerCommand(QUndoCommand):
    def __init__(self, item, old_pos, new_pos, description="Move Layer"):
        super().__init__(description)
        self.item = item
        self.old_pos = old_pos
        self.new_pos = new_pos
        
    def redo(self):
        self.item.setPos(self.new_pos)
        
    def undo(self):
        self.item.setPos(self.old_pos)

class TextChangeCommand(QUndoCommand):
    def __init__(self, item, old_text, new_text, description="Edit Text"):
        super().__init__(description)
        self.item = item
        self.old_text = old_text
        self.new_text = new_text
        
    def redo(self):
        self.item.setPlainText(self.new_text)
        
    def undo(self):
        self.item.setPlainText(self.old_text)

class PropertyChangeCommand(QUndoCommand):
    def __init__(self, item, property_name, old_value, new_value, description="Change Property"):
        super().__init__(description)
        self.item = item
        self.property_name = property_name
        self.old_value = old_value
        self.new_value = new_value
        
    def redo(self):
        self._apply(self.new_value)
        
    def undo(self):
        self._apply(self.old_value)
        
    def _apply(self, value):
        if self.property_name == 'font_family':
            font = self.item.font()
            font.setFamily(value)
            self.item.setFont(font)
        elif self.property_name == 'font_size':
            font = self.item.font()
            font.setPointSize(value)
            self.item.setFont(font)
        elif self.property_name == 'bold':
            font = self.item.font()
            font.setBold(value)
            self.item.setFont(font)
        elif self.property_name == 'italic':
            font = self.item.font()
            font.setItalic(value)
            self.item.setFont(font)
        elif self.property_name == 'color':
            self.item.setDefaultTextColor(value)
