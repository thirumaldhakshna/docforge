import json
import os

class ProjectService:
    @staticmethod
    def save_project(path, data):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            
    @staticmethod
    def load_project(path):
        if not os.path.exists(path):
            raise FileNotFoundError("Project file not found.")
            
        with open(path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                raise ValueError("Corrupted or invalid project file format.")
                
        if not isinstance(data, dict):
            raise ValueError("Invalid project data structure.")
            
        required_keys = ['mode', 'layers']
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key in project file: {key}")
                
        return data
