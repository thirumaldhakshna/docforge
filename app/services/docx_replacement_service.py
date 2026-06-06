import re
import logging
import traceback

class DocxReplacementService:
    def __init__(self):
        self.pattern_curly = re.compile(r'\{\{([^}]+)\}\}')
        self.pattern_dollar = re.compile(r'\$([a-zA-Z0-9_]+)')

    def replace_variables_in_doc(self, doc, row_data):
        
        def process_paragraph(paragraph):
            try:
                if not paragraph.text: return
                if not ('{{' in paragraph.text or '$' in paragraph.text):
                    return
                
                text = ""
                run_map = [] 
                for r_idx, run in enumerate(paragraph.runs):
                    run_text = str(run.text) if run.text else ""
                    for char in run_text:
                        run_map.append(r_idx)
                    text += run_text
                    
                if not text:
                    return
                    
                matches = list(self.pattern_curly.finditer(text)) + list(self.pattern_dollar.finditer(text))
                if not matches:
                    return
                    
                matches.sort(key=lambda m: m.start())
                
                resolved_matches = []
                last_end = 0
                for m in matches:
                    if m.start() >= last_end:
                        resolved_matches.append(m)
                        last_end = m.end()
                        
                if not resolved_matches:
                    return
                    
                replacements = {}
                for m in resolved_matches:
                    var_name = m.group(1).strip()
                    replacement_text = str(row_data.get(var_name, m.group(0)))
                    replacements[m.start()] = replacement_text
                    
                    logging.info(f"DOCX Replace - placeholder: '{m.group(0)}', replaced with: '{replacement_text}'")
                    
                run_new_texts = {r_idx: [] for r_idx in range(len(paragraph.runs))}
                
                i = 0
                while i < len(text):
                    match_here = next((m for m in resolved_matches if m.start() == i), None)
                    
                    if match_here:
                        r_idx = run_map[i]
                        run_new_texts[r_idx].append(str(replacements[i]))
                        i = match_here.end() 
                    else:
                        r_idx = run_map[i]
                        run_new_texts[r_idx].append(str(text[i]))
                        i += 1
                        
                for r_idx, run in enumerate(paragraph.runs):
                    original_text = str(run.text) if run.text else ""
                    new_text = "".join(run_new_texts[r_idx])
                    if original_text != new_text:
                        logging.debug(f"Run {r_idx} text changed from '{original_text}' to '{new_text}'")
                    run.text = new_text
            except Exception as e:
                err_tb = traceback.format_exc()
                logging.error(f"Error processing paragraph in DOCX replacement:\n{err_tb}")

        try:
            for para in doc.paragraphs:
                process_paragraph(para)
                
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for para in cell.paragraphs:
                            process_paragraph(para)
        except Exception as e:
            err_tb = traceback.format_exc()
            logging.error(f"Critical failure in DOCX replacement engine:\n{err_tb}")
            raise
