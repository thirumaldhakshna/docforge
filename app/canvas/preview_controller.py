import os
from PyQt6.QtCore import QObject, pyqtSignal
from app.services.pdf_renderer import PDFRenderer
from app.services.docx_preview_service import DocxPreviewService

class PreviewController(QObject):
    preview_updated = pyqtSignal(bool, str) # has_preview, message
    
    def __init__(self, scene):
        super().__init__()
        self.scene = scene
        self.renderer = PDFRenderer()
        self.docx_service = DocxPreviewService()
        self.current_file = None
        
    def load_file(self, filepath):
        self.current_file = filepath
        if not filepath or not os.path.exists(filepath):
            self.scene.set_preview_pixmap(None)
            self.preview_updated.emit(False, "")
            return
            
        _, ext = os.path.splitext(filepath.lower())
        
        try:
            render_path = filepath
            if ext == '.docx':
                self.preview_updated.emit(False, "Converting DOCX for preview...\nThis may take a moment.")
                from PyQt6.QtWidgets import QApplication
                QApplication.processEvents()
                
                try:
                    render_path = self.docx_service.create_preview_pdf(filepath)
                except (FileNotFoundError, ValueError):
                    self.scene.set_preview_pixmap(None)
                    self.preview_updated.emit(False, "DOCX converted unsuccessfully. PDF file was not created.")
                    return
                except Exception as e:
                    self.scene.set_preview_pixmap(None)
                    self.preview_updated.emit(False, f"DOCX preview conversion failed:\n{str(e)}")
                    return
                
            if not os.path.exists(render_path) or os.path.getsize(render_path) == 0:
                self.scene.set_preview_pixmap(None)
                if ext == '.docx':
                    self.preview_updated.emit(False, "DOCX converted unsuccessfully. PDF file was not created.")
                else:
                    self.preview_updated.emit(False, "Failed to load document. File is missing or empty.")
                return
                
            success = self.renderer.load_document(render_path)
            if not success:
                self.scene.set_preview_pixmap(None)
                if ext == '.docx':
                    self.preview_updated.emit(False, "Generated PDF is corrupted or unreadable.\nCheck terminal logs for PyMuPDF diagnostics.")
                else:
                    self.preview_updated.emit(False, "Failed to load document.\nCheck terminal logs for PyMuPDF diagnostics.")
                return
                
            pixmap = self.renderer.render_page(0, zoom=2.0)
            if pixmap and not pixmap.isNull():
                self.scene.set_preview_pixmap(pixmap)
                self.preview_updated.emit(True, "")
            else:
                self.scene.set_preview_pixmap(None)
                self.preview_updated.emit(False, "Failed to render page to QPixmap. Check terminal logs.")
                
        except Exception as e:
            self.scene.set_preview_pixmap(None)
            if ext == '.docx':
                self.preview_updated.emit(False, f"DOCX preview conversion failed:\n{str(e)}")
            else:
                self.preview_updated.emit(False, f"Error: {str(e)}")
