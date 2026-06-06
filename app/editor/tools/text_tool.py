from app.editor.items.text_layer_item import TextLayerItem

class TextTool:
    def __init__(self, scene):
        self.scene = scene

    def execute(self):
        return self.scene.add_text_layer("Text", center=True)
