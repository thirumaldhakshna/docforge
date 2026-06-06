import os
from docx import Document
from app.services.docx_replacement_service import DocxReplacementService
from docx2pdf import convert
import logging

class DocxExporter:
    def __init__(self):
        self.replacement_service = DocxReplacementService()

    @staticmethod
    def sanitize_filename(filename):
        import re
        return re.sub(r'[<>:"/\\|?*]', '_', str(filename))

    def export_bulk_docx(self, template_path, excel_rows, output_dir, output_format="docx", progress_callback=None, cancel_callback=None):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        total = len(excel_rows)
        output_paths = []
        for i, row in enumerate(excel_rows):
            if cancel_callback and cancel_callback():
                break
                
            doc = Document(template_path)
            self.replacement_service.replace_variables_in_doc(doc, row)
            
            name_val = row.get('name')
            if name_val:
                fname = f"{self.sanitize_filename(name_val)}"
            else:
                fname = f"document_{i+1}"
                
            docx_out_path = os.path.join(output_dir, fname + ".docx")
            
            counter = 1
            base_fname = fname
            while os.path.exists(docx_out_path):
                fname = f"{base_fname}_{counter}"
                docx_out_path = os.path.join(output_dir, fname + ".docx")
                counter += 1
                
            doc.save(docx_out_path)
            
            if output_format == "pdf":
                pdf_out_path = os.path.join(output_dir, fname + ".pdf")
                try:
                    import sys
                    import io
                    from contextlib import redirect_stdout, redirect_stderr
                    dummy_out = io.StringIO()
                    dummy_err = io.StringIO()
                    with redirect_stdout(dummy_out), redirect_stderr(dummy_err):
                        convert(os.path.abspath(docx_out_path), os.path.abspath(pdf_out_path))
                        
                    if os.path.exists(docx_out_path):
                        os.remove(docx_out_path)
                    output_paths.append(pdf_out_path)
                except Exception as e:
                    logging.error(f"Failed to convert {fname} to PDF: {e}")
                    output_paths.append(docx_out_path)
            else:
                output_paths.append(docx_out_path)
            
            if progress_callback:
                progress_callback(i + 1, total)

        return output_paths

    def export_combined_docx(self, template_path, excel_rows, output_dir, output_format="docx", progress_callback=None, cancel_callback=None):
        logging.info(f"DocxExporter.export_combined_docx initialized. Template: {template_path}, Rows: {len(excel_rows)}, Output Dir: {output_dir}, Output Format: {output_format}")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        if not excel_rows:
            return None
            
        from docxcompose.composer import Composer
        
        master_doc = None
        composer = None
        
        total = len(excel_rows)
        for i, row in enumerate(excel_rows):
            if cancel_callback and cancel_callback():
                break
                
            doc = Document(template_path)
            self.replacement_service.replace_variables_in_doc(doc, row)
            
            if i == 0:
                master_doc = doc
                composer = Composer(master_doc)
            else:
                master_doc.add_page_break()
                composer.append(doc)
                
            if progress_callback:
                progress_callback(i + 1, total)
                
        if cancel_callback and cancel_callback():
            return None
            
        if master_doc:
            fname = "combined_output"
            docx_out_path = os.path.join(output_dir, fname + ".docx")
            
            counter = 1
            base_fname = fname
            while os.path.exists(docx_out_path):
                fname = f"{base_fname}_{counter}"
                docx_out_path = os.path.join(output_dir, fname + ".docx")
                counter += 1
                
            master_doc.save(docx_out_path)
            
            if output_format == "pdf":
                pdf_out_path = os.path.join(output_dir, fname + ".pdf")
                try:
                    import sys
                    import io
                    from contextlib import redirect_stdout, redirect_stderr
                    dummy_out = io.StringIO()
                    dummy_err = io.StringIO()
                    with redirect_stdout(dummy_out), redirect_stderr(dummy_err):
                        convert(os.path.abspath(docx_out_path), os.path.abspath(pdf_out_path))
                        
                    if os.path.exists(docx_out_path):
                        os.remove(docx_out_path)
                    return pdf_out_path
                except Exception as e:
                    logging.error(f"Failed to convert combined DOCX to PDF: {e}")
                    return docx_out_path

            return docx_out_path

        return None
