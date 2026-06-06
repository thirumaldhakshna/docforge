import pandas as pd

class ExcelService:
    @staticmethod
    def get_columns(path):
        try:
            df = pd.read_excel(path, nrows=0)
            return [str(col).strip() for col in df.columns]
        except Exception as e:
            raise ValueError(f"Invalid Excel file: {e}")

    @staticmethod
    def load_excel(path):
        try:
            df = pd.read_excel(path)
            
            # Strip column names
            df.columns = [str(col).strip() for col in df.columns]
            
            # Remove empty rows
            df.dropna(how='all', inplace=True)
            
            # Replace NaN with empty string
            df.fillna("", inplace=True)
            
            return df.to_dict('records')
        except Exception as e:
            raise ValueError(f"Error loading Excel: {e}")
