from app.export.pdf_exporter import PDFExporter

class ExportWorker:
    def __init__(self, pdf_template_path, layers, excel_rows, output_dir, ui_rect, export_type="separate"):
        self.pdf_template_path = pdf_template_path
        self.layers = layers
        self.excel_rows = excel_rows
        self.output_dir = output_dir
        self.ui_rect = ui_rect
        self.export_type = export_type
        self.exporter = PDFExporter()
        self.is_cancelled = False
        
    def run(self, progress_callback=None):
        if self.export_type == "combined":
            return self.exporter.export_combined_pdf(
                self.pdf_template_path,
                self.layers,
                self.excel_rows,
                self.output_dir,
                self.ui_rect,
                progress_callback=progress_callback,
                cancel_callback=lambda: self.is_cancelled
            )
        else:
            return self.exporter.export_bulk_pdfs(
                self.pdf_template_path,
                self.layers,
                self.excel_rows,
                self.output_dir,
                self.ui_rect,
                progress_callback=progress_callback,
                cancel_callback=lambda: self.is_cancelled
            )
        
    def cancel(self):
        self.is_cancelled = True
