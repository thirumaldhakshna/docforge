import fitz
import os
import logging
import traceback
import shutil
from PyQt6.QtGui import QImage, QPixmap

class PDFRenderer:
    def __init__(self):
        self.doc = None

    def load_document(self, path):
        if self.doc:
            self.doc.close()
            self.doc = None
            
        logging.info(f"PDFRenderer.load_document called for path: {path}")
        exists = os.path.exists(path)
        size = os.path.getsize(path) if exists else 0
        logging.info(f"File Exists: {exists}, File Size: {size} bytes")
        
        if not exists or size == 0:
            logging.error("PDFRenderer: File is missing or empty.")
            return False
            
        try:
            self.doc = fitz.open(path)
            logging.info(f"PDFRenderer: Opened document. Page count: {len(self.doc)}")
            if len(self.doc) > 0:
                first_page = self.doc[0]
                logging.info(f"PDFRenderer: First page dimensions: {first_page.rect}")
            return True
        except Exception as e:
            err_tb = traceback.format_exc()
            logging.error(f"PDFRenderer: fitz.open() failed:\n{err_tb}")
            
            try:
                diag_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "diagnostics")
                if not os.path.exists(diag_dir):
                    os.makedirs(diag_dir)
                diag_path = os.path.join(diag_dir, "corrupted_" + os.path.basename(path))
                shutil.copy2(path, diag_path)
                logging.error(f"PDFRenderer: Copied corrupted PDF to diagnostics folder: {diag_path}")
            except Exception as copy_e:
                logging.error(f"PDFRenderer: Failed to copy corrupted PDF to diagnostics: {copy_e}")
                
            return False

    def render_page(self, page_number=0, zoom=1.0):
        if not self.doc or page_number >= len(self.doc):
            logging.error(f"PDFRenderer: render_page failed. doc is None or page {page_number} out of bounds.")
            return None
            
        try:
            page = self.doc.load_page(page_number)
            
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # If image DPI > 150: Automatically downscale preview rendering to avoid OOM
            if pix.xres > 150 or pix.yres > 150:
                scale_factor = 150.0 / max(pix.xres, pix.yres)
                downscale_mat = fitz.Matrix(zoom * scale_factor, zoom * scale_factor)
                pix = None  # Free previous
                pix = page.get_pixmap(matrix=downscale_mat, alpha=False)
            
            # Also cap massive dimensions
            if pix.width * pix.height > 15000000:  # ~15 MP
                scale_factor = (15000000 / (pix.width * pix.height)) ** 0.5
                downscale_mat = fitz.Matrix(zoom * scale_factor, zoom * scale_factor)
                pix = None
                pix = page.get_pixmap(matrix=downscale_mat, alpha=False)
            
            if not pix or pix.width == 0 or pix.height == 0:
                logging.error("PDFRenderer: get_pixmap returned invalid or 0-size pixmap.")
                return None
                
            # Add requested debug logging
            try:
                blocks = page.get_text("dict").get("blocks", [])
                text_blocks = sum(1 for b in blocks if b.get("type") == 0)
                image_blocks = sum(1 for b in blocks if b.get("type") == 1)
                logging.info(f"PDFRenderer: Page dimensions: {page.rect}")
                logging.info(f"PDFRenderer: Extracted text blocks: {text_blocks}, images: {image_blocks}")
            except Exception as d_err:
                logging.warning(f"PDFRenderer: Could not extract block info: {d_err}")
                
            # FIX: Prevent premature garbage collection of pix.samples bytes object
            samples = pix.samples
            img = QImage(samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
            img = img.copy() # Deep copy to detach from Python memory
            
            pixmap = QPixmap.fromImage(img)
            
            # Explicitly release memory
            samples = None
            pix = None
            
            if pixmap.isNull():
                logging.error("PDFRenderer: QPixmap.fromImage returned a null QPixmap. Possibly unsupported image format or corrupted memory.")
                return None
                
            logging.info("PDFRenderer: Canvas draw operations prepared (Pixmap generated successfully).")
            return pixmap
        except Exception as e:
            err_tb = traceback.format_exc()
            logging.error(f"PDFRenderer: Exception during render_page:\n{err_tb}")
            return None
        
    def __del__(self):
        if self.doc:
            try:
                self.doc.close()
            except:
                pass
