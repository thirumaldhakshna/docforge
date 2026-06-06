import re

class VariableService:
    def __init__(self):
        # Matches {{var}} and $var
        self.pattern_curly = re.compile(r'\{\{([^}]+)\}\}')
        self.pattern_dollar = re.compile(r'\$([a-zA-Z0-9_]+)')

    def extract_variables(self, text):
        if not text:
            return []
        vars_curly = self.pattern_curly.findall(text)
        vars_dollar = self.pattern_dollar.findall(text)
        
        all_vars = [self.normalize_variable(v) for v in vars_curly + vars_dollar]
        return list(set(all_vars))

    def normalize_variable(self, name):
        return str(name).strip()

    def find_missing_variables(self, texts, columns):
        all_vars = set()
        for text in texts:
            all_vars.update(self.extract_variables(text))
            
        columns_set = set([self.normalize_variable(c) for c in columns])
        
        missing = [v for v in all_vars if v not in columns_set]
        return sorted(missing)
