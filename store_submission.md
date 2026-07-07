# Publishing DocForge to the Microsoft Store

This guide walks you through submitting DocForge as an MSIX package to the Microsoft Store.

---

## Prerequisites

- [ ] Windows 10/11 machine with Windows 10 SDK installed
- [ ] Python environment with PyInstaller
- [ ] Microsoft Partner Center developer account

---

## Step 1: Create a Microsoft Partner Center Account

1. Go to [Microsoft Partner Center](https://partner.microsoft.com/dashboard)
2. Sign in with your Microsoft account
3. Navigate to **Windows & Xbox** → **Overview**
4. If not enrolled, click **Register** as an individual developer
   - One-time registration fee: **$19 USD**
   - Provide your developer details (name, email, country)
5. Wait for account verification (usually instant for individuals)

---

## Step 2: Reserve Your App Name

1. In Partner Center, go to **Apps and games** → **New product** → **App**
2. Enter **"DocForge"** as the product name
3. Click **Reserve product name**
4. If "DocForge" is taken, try alternatives like:
   - "DocForge - Document Automation"
   - "DocForge PDF & DOCX Generator"

> **Important:** Once reserved, the name is held for 1 year. You must submit a package within that time.

---

## Step 3: Update the MSIX Identity

After reserving your app name, Partner Center will provide:
- **Package/Identity/Name** (e.g., `12345ThirumalDhakshnamoorthy.DocForge`)
- **Package/Identity/Publisher** (e.g., `CN=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`)
- **Package/Properties/PublisherDisplayName**

Update these values in `msix/AppxManifest.xml`:

```xml
<Identity Name="YOUR_PACKAGE_IDENTITY_NAME"
          Publisher="YOUR_PUBLISHER_ID_FROM_PARTNER_CENTER"
          Version="2.0.0.0"
          ProcessorArchitecture="x64" />
```

And update the build script parameters:
```powershell
.\build_msix.ps1 -Publisher "CN=YOUR_PUBLISHER_ID" -Version "2.0.0.0" -SkipSign
```

> **Note:** Use `-SkipSign` for Store submissions. Microsoft signs the package during certification.

---

## Step 4: Build the MSIX Package

```powershell
# Full build (PyInstaller + MSIX)
.\build_msix.ps1 -SkipSign

# Or if you already have dist\DocForge\ built:
.\build_msix.ps1 -SkipBuild -SkipSign
```

The output `.msix` file will be in `msix_output\`.

---

## Step 5: Create the Store Listing

In Partner Center, fill out the following for your app submission:

### Properties
| Field | Value |
|-------|-------|
| Category | **Business** or **Productivity** |
| Sub-category | **Collaboration** or leave blank |
| Privacy policy URL | Your privacy policy URL |
| Website | `https://github.com/thirumaldhakshna/docforge` |

### Age Ratings
1. Complete the **IARC questionnaire**
2. DocForge should qualify for **3+** (no objectionable content)

### Pricing
| Field | Value |
|-------|-------|
| Base price | **Free** (recommended for initial launch) |
| Free trial | N/A (already free) |
| Markets | **All available markets** |

### Store Listing (en-us)

**Description (required):**
```
DocForge is an advanced PDF & DOCX template automation platform. Generate personalized documents in bulk from templates using spreadsheet data.

Key Features:
• DOCX Mode — Replace tags in DOCX templates with rows of data from Excel/CSV spreadsheets
• PDF Designer Mode — Visually map spreadsheet columns to specific locations on a PDF template
• Bulk Export — Automatically generate individual files for each row of your dataset
• Intuitive drag-and-drop interface for positioning text on PDF templates
• Support for Excel (.xlsx) and CSV data sources

Perfect for:
• Generating personalized certificates, letters, and invoices
• Mail merge workflows with visual PDF positioning
• Batch document creation from spreadsheet data
```

**Short description:**
```
Generate personalized PDF & DOCX documents in bulk from templates and spreadsheet data.
```

**Search terms (max 7, each max 30 characters):**
```
PDF template
document automation
mail merge
bulk document generator
DOCX template
certificate generator
spreadsheet to PDF
```

**Screenshots (required):**
- Minimum 1 screenshot, recommended 4-5
- Size: 1366×768 or 2732×1536 (16:9 ratio)
- Capture the main UI, DOCX mode, PDF designer, and export dialog
- Use Windows Snipping Tool or `Win + Shift + S`

**App icon (Store listing):**
- 300×300 PNG with transparent background
- Use `assets\icons\app_512.png` resized to 300×300

---

## Step 6: Upload the MSIX Package

1. In your app submission, go to **Packages**
2. Click **Browse files** and select `msix_output\DocForge_v2.0.0.0.msix`
3. Wait for validation to complete (checks manifest, assets, etc.)
4. If validation fails, check the error details and fix accordingly

### Common Validation Errors

| Error | Fix |
|-------|-----|
| Publisher mismatch | Update `Publisher` in manifest to match Partner Center |
| Missing assets | Ensure all required logo sizes are in the package |
| Invalid version | Version must be in `X.X.X.X` format |
| Package already exists | Increment the version number |

---

## Step 7: Submit for Certification

1. Review all sections show a green checkmark ✅
2. Click **Submit to the Store**
3. Certification typically takes **1-3 business days**
4. You'll receive an email when certification completes

### Certification Requirements
- App must not crash on launch
- App must match the Store description
- No malware or deceptive behavior
- Privacy policy if collecting data
- Must work on declared OS versions

---

## Step 8: Post-Launch

### Updating Your App
1. Increment version in `version.py` and `AppxManifest.xml`
2. Rebuild: `.\build_msix.ps1 -SkipSign`
3. Create a new submission in Partner Center
4. Upload the new `.msix` package
5. Submit for certification

### Monitoring
- Check **Analytics** in Partner Center for downloads, ratings, and crash reports
- Respond to user reviews
- Monitor health reports for crashes

---

## File Structure

```
docforge/
├── msix/
│   ├── AppxManifest.xml          # MSIX package manifest
│   └── Assets/                    # Generated logo assets
│       ├── Square44x44Logo.png
│       ├── Square150x150Logo.png
│       ├── Wide310x150Logo.png
│       ├── LargeTile.png
│       ├── StoreLogo.png
│       └── SplashScreen.png
├── build_msix.ps1                 # Build automation script
├── msix_output/                   # Build output (gitignored)
│   ├── PackageLayout/             # MSIX package contents
│   ├── DocForge_v2.0.0.0.msix    # Final MSIX package
│   ├── DocForge_Dev.pfx           # Dev signing certificate
│   └── DocForge_Dev.cer           # Public certificate
├── store_submission.md            # This file
└── ...
```

---

## Troubleshooting

### "makeappx.exe not found"
Install the Windows 10 SDK from:
https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/

### "The package could not be opened"
- Verify the `AppxManifest.xml` is valid XML
- Check all referenced asset files exist in the package
- Ensure version format is `X.X.X.X`

### "Publisher mismatch during signing"
The certificate subject must exactly match the `Publisher` attribute in the manifest.

### App doesn't appear in Start Menu after install
- Check that `Executable` in the manifest points to the correct exe name
- Verify `EntryPoint` is set to `Windows.FullTrustApplication`

### Certification failed
- Review the certification report in Partner Center
- Common issues: crashes on clean Windows install, missing redistributables
- Test on a clean VM before submitting
