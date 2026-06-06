# DocForge

DocForge is an advanced PDF & DOCX template automation platform. It allows users to generate personalized documents (PDF and DOCX) in bulk from templates using spreadsheet data.

## Features
- **DOCX Mode:** Replace tags in DOCX templates with rows of data from an Excel/CSV spreadsheet.
- **PDF Designer Mode:** Visually map spreadsheet columns to locations on a PDF template.
- **Bulk Export:** Automatically generate individual files for each row of your dataset.

## Installation

1. Clone the repository.
2. Create and activate a virtual environment.
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install the dependencies.
   ```cmd
   pip install -r requirements.txt
   ```

## Running the Application

To launch DocForge:
```cmd
python main.py
```

## Build Executable

To build a standalone executable:
```cmd
pyinstaller DocForge.spec
```
