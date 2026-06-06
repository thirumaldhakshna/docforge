import fitz
import os
import re
from app.export.coordinate_mapper import CoordinateMapper

class PDFExporter:
    @staticmethod
    def replace_variables(text, row_data):
        # Replace {{var}}
        def replacer_curly(match):
            var_name = match.group(1).strip()
            return str(row_data.get(var_name, match.group(0)))
            
        text = re.sub(r'\{\{([^}]+)\}\}', replacer_curly, text)
        
        # Replace $var
        def replacer_dollar(match):
            var_name = match.group(1).strip()
            return str(row_data.get(var_name, match.group(0)))
            
        text = re.sub(r'\$([a-zA-Z0-9_]+)', replacer_dollar, text)
        return text

    @staticmethod
    def sanitize_filename(filename):
        return re.sub(r'[<>:"/\\|?*]', '_', str(filename))

    @staticmethod
    def resolve_font(page, family, bold, italic):
        family_lower = str(family).lower()
        import os
        import logging
        
        # 1. Base-14 Mappings
        if "times" in family_lower:
            if bold and italic: return "tibi"
            if bold: return "tibo"
            if italic: return "tiit"
            return "tiro"
        if "arial" in family_lower or "helvetica" in family_lower:
            if bold and italic: return "hebi"
            if bold: return "hebo"
            if italic: return "heit"
            return "helv"
        if "courier" in family_lower:
            if bold and italic: return "cobi"
            if bold: return "cobo"
            if italic: return "coit"
            return "cour"
            
        # 2. Local TTF resolution on Windows
        font_dir = "C:\\Windows\\Fonts"
        filename = None
        
        if "calibri" in family_lower:
            if bold and italic: filename = "calibriz.ttf"
            elif bold: filename = "calibrib.ttf"
            elif italic: filename = "calibrii.ttf"
            else: filename = "calibri.ttf"
        elif "cambria" in family_lower:
            if bold and italic: filename = "cambriaz.ttf"
            elif bold: filename = "cambriab.ttf"
            elif italic: filename = "cambriai.ttf"
            else: filename = "cambria.ttc"
        elif "segoe" in family_lower:
            if bold and italic: filename = "segoeuiz.ttf"
            elif bold: filename = "segoeuib.ttf"
            elif italic: filename = "segoeuii.ttf"
            else: filename = "segoeui.ttf"
        elif "verdana" in family_lower:
            if bold and italic: filename = "verdanaz.ttf"
            elif bold: filename = "verdanab.ttf"
            elif italic: filename = "verdanai.ttf"
            else: filename = "verdana.ttf"
        elif "tahoma" in family_lower:
            if bold: filename = "tahomabd.ttf"
            else: filename = "tahoma.ttf"
            
        if filename:
            filepath = os.path.join(font_dir, filename)
            if os.path.exists(filepath):
                internal_name = f"f_{family_lower.replace(' ', '')}_{'b' if bold else ''}{'i' if italic else ''}"
                try:
                    page.insert_font(fontname=internal_name, fontfile=filepath)
                    return internal_name
                except Exception as e:
                    logging.warning(f"Failed to embed font {filename}: {e}")
            else:
                logging.warning(f"Font file {filename} not found in {font_dir}. Using fallback.")
                
        # 3. Fallback
        logging.warning(f"Font '{family}' unavailable. Using Helvetica fallback.")
        if bold and italic: return "hebi"
        if bold: return "hebo"
        if italic: return "heit"
        return "helv"

    def export_bulk_pdfs(self, pdf_template_path, layers, excel_rows, output_dir, ui_rect, progress_callback=None, cancel_callback=None):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        total_rows = len(excel_rows)
        output_paths = []
        
        # Open a dummy document just to extract the native page 0 rect
        doc_temp = fitz.open(pdf_template_path)
        pdf_rect = doc_temp[0].rect
        mapper = CoordinateMapper(ui_rect, pdf_rect)
        doc_temp.close()

        try:
            for i, row in enumerate(excel_rows):
                if cancel_callback and cancel_callback():
                    break
                    
                import logging
                logging.info(f"PDFExporter: Processing row {i+1}/{total_rows}")
                
                doc = fitz.open(pdf_template_path)
            
            # Map and stamp each layer
            for layer in layers:
                page_num = layer.get('page_number', 0)
                if page_num >= len(doc):
                    continue
                    
                page = doc[page_num]
                
                text = self.replace_variables(layer.get('text', ''), row)
                
                x1 = mapper.map_x(layer['x'])
                y1 = mapper.map_y(layer['y'])
                w = mapper.map_x(layer.get('width', 200))
                h = mapper.map_y(layer.get('height', 50))
                
                # Expand rect aggressively to prevent PyMuPDF from silently dropping text
                # due to minor font-metric kerning differences between Qt and PDF
                rect = fitz.Rect(x1, y1, x1 + w + 500, y1 + h + 500)
                
                font_size = mapper.map_font_size(layer['font_size'])
                color_hex = layer['color'].lstrip('#')
                color = tuple(int(color_hex[i:i+2], 16)/255.0 for i in (0, 2, 4))
                
                font_family = layer.get('font_family', 'Helvetica')
                bold = layer.get('bold', False)
                italic = layer.get('italic', False)
                fontname = self.resolve_font(page, font_family, bold, italic)
                
                import logging
                logging.info(f"Text: {text}")
                logging.info(f"Font: {font_family}")
                logging.info(f"Size: {layer.get('font_size', 14)}")
                logging.info(f"Bold: {bold}")
                logging.info(f"Italic: {italic}")
                logging.info(f"Color: {layer.get('color', '#000000')}")
                    
                # insert_textbox handles multi-line layout and aligns perfectly with the boundingRect
                page.insert_textbox(rect, text, fontsize=font_size, fontname=fontname, color=color)

            import logging
            logging.info("Exported page overlays applied: YES")

            name_val = row.get('name')
            if name_val:
                fname = f"{self.sanitize_filename(name_val)}.pdf"
            else:
                fname = f"document_{i+1}.pdf"
                
            out_path = os.path.join(output_dir, fname)
            
            counter = 1
            base_fname = fname
            while os.path.exists(out_path):
                name, ext = os.path.splitext(base_fname)
                fname = f"{name}_{counter}{ext}"
                out_path = os.path.join(output_dir, fname)
                counter += 1
                
            doc.save(out_path)
            doc.close()
            output_paths.append(out_path)
            
            if progress_callback:
                progress_callback(i + 1, total_rows)

        except RuntimeError as e:
            if "code=2" in str(e) or "realloc" in str(e):
                import logging
                logging.error(f"Memory allocation failed at row {i+1}: {e}")
                raise Exception("PDF template is too large to process.\nTry reducing PDF size or page count.")
            raise
            
        return output_paths

    def export_combined_pdf(self, pdf_template_path, layers, excel_rows, output_dir, ui_rect, progress_callback=None, cancel_callback=None):
        import logging
        logging.info(f"PDFExporter.export_combined_pdf initialized. Template: {pdf_template_path}, Rows: {len(excel_rows)}, Output Dir: {output_dir}")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        total_rows = len(excel_rows)
        
        doc_temp = fitz.open(pdf_template_path)
        pdf_rect = doc_temp[0].rect
        mapper = CoordinateMapper(ui_rect, pdf_rect)
        doc_temp.close()
        
        fname = "combined_output.pdf"
        out_path = os.path.join(output_dir, fname)
        
        counter = 1
        base_fname = "combined_output"
        while os.path.exists(out_path):
            fname = f"{base_fname}_{counter}.pdf"
            out_path = os.path.join(output_dir, fname)
            counter += 1

        import tempfile
        import shutil

        try:
            for i, row in enumerate(excel_rows):
                if cancel_callback and cancel_callback():
                    return None
                    
                logging.info(f"PDFExporter: Processing row {i+1}/{total_rows}")
                
                doc = fitz.open(pdf_template_path)
            
                for layer in layers:
                    page_num = layer.get('page_number', 0)
                    if page_num >= len(doc):
                        continue
                        
                    page = doc[page_num]
                    
                    text = self.replace_variables(layer.get('text', ''), row)
                    
                    x1 = mapper.map_x(layer['x'])
                    y1 = mapper.map_y(layer['y'])
                    w = mapper.map_x(layer.get('width', 200))
                    h = mapper.map_y(layer.get('height', 50))
                    
                    rect = fitz.Rect(x1, y1, x1 + w + 500, y1 + h + 500)
                    
                    font_size = mapper.map_font_size(layer['font_size'])
                    color_hex = layer['color'].lstrip('#')
                    color = tuple(int(color_hex[j:j+2], 16)/255.0 for j in (0, 2, 4))
                    
                    font_family = layer.get('font_family', 'Helvetica')
                    bold = layer.get('bold', False)
                    italic = layer.get('italic', False)
                    fontname = self.resolve_font(page, font_family, bold, italic)
                    
                    import logging
                    logging.info(f"Text: {text}")
                    logging.info(f"Font: {font_family}")
                    logging.info(f"Size: {layer.get('font_size', 14)}")
                    logging.info(f"Bold: {bold}")
                    logging.info(f"Italic: {italic}")
                    logging.info(f"Color: {layer.get('color', '#000000')}")
                        
                    page.insert_textbox(rect, text, fontsize=font_size, fontname=fontname, color=color)

                logging.info("Exported page overlays applied: YES")

                temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
                os.close(temp_fd)
                doc.save(temp_path)
                doc.close()

                if i == 0:
                    shutil.move(temp_path, out_path)
                else:
                    master_doc = fitz.open(out_path)
                    temp_doc = fitz.open(temp_path)
                    master_doc.insert_pdf(temp_doc)
                    master_doc.saveIncr()
                    temp_doc.close()
                    master_doc.close()
                    os.remove(temp_path)
            
                if progress_callback:
                    progress_callback(i + 1, total_rows)
                    
        except RuntimeError as e:
            if "code=2" in str(e) or "realloc" in str(e):
                logging.error(f"Memory allocation failed at row {i+1}: {e}")
                raise Exception("PDF template is too large to process.\nTry reducing PDF size or page count.")
            raise
            
        return out_path
