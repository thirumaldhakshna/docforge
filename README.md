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

## Build MSIX Package (Microsoft Store)

DocForge can be packaged as an MSIX for the Microsoft Store or sideloading.

**Prerequisites:**
- Windows 10 SDK ([download](https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/))
- PyInstaller (`pip install pyinstaller`)

**Build the MSIX package:**
```powershell
# Full build (PyInstaller + MSIX packaging)
.\build_msix.ps1

# Skip PyInstaller if you already have dist\DocForge\
.\build_msix.ps1 -SkipBuild

# Skip signing (for Microsoft Store submission — Microsoft signs it)
.\build_msix.ps1 -SkipSign
```

The output `.msix` file will be in `msix_output\`.

**For detailed Microsoft Store publishing instructions, see [store_submission.md](store_submission.md).**
