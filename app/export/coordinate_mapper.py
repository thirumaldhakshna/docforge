class CoordinateMapper:
    def __init__(self, ui_rect, pdf_rect):
        # Scale ratio mapping UI Canvas Pixel space -> Native PDF Point space
        self.scale_x = pdf_rect.width / ui_rect.width() if ui_rect.width() else 1.0
        self.scale_y = pdf_rect.height / ui_rect.height() if ui_rect.height() else 1.0

    def map_x(self, x):
        return x * self.scale_x

    def map_y(self, y):
        return y * self.scale_y

    def map_font_size(self, size):
        # Scale the font size relative to the document size proportion
        return size * self.scale_y
