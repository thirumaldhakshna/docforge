<#
.SYNOPSIS
    Build script for creating an MSIX package of DocForge for Microsoft Store.

.DESCRIPTION
    This script automates the full pipeline:
    1. Builds the PyInstaller executable
    2. Generates MSIX logo assets from the app icon
    3. Assembles the MSIX package layout
    4. Creates a self-signed certificate (for dev/sideloading)
    5. Packages everything into an .msix file
    6. Signs the package

.NOTES
    Prerequisites:
    - Python with PyInstaller installed
    - Windows 10 SDK (provides makeappx.exe and signtool.exe)
    - PowerShell 5.1+

.EXAMPLE
    .\build_msix.ps1
    .\build_msix.ps1 -SkipBuild        # Skip PyInstaller, use existing dist\
    .\build_msix.ps1 -SkipSign          # Skip signing (for Partner Center submission)
#>

param(
    [switch]$SkipBuild,
    [switch]$SkipSign,
    [string]$CertificatePassword = "DocForge2024!",
    [string]$Publisher = "CN=Thirumal Dhakshnamoorthy",
    [string]$Version = "1.0.0.0"
)

$ErrorActionPreference = "Stop"

# ── Paths ────────────────────────────────────────────────────────────────────
$ProjectRoot   = Split-Path -Parent $MyInvocation.MyCommand.Path
$DistDir       = Join-Path $ProjectRoot "dist\DocForge"
$MsixSourceDir = Join-Path $ProjectRoot "msix"
$MsixAssetsDir = Join-Path $MsixSourceDir "Assets"
$OutputDir     = Join-Path $ProjectRoot "msix_output"
$PackageLayout = Join-Path $OutputDir "PackageLayout"
$MsixFile      = Join-Path $OutputDir "DocForge_v$Version.msix"
$CertFile      = Join-Path $OutputDir "DocForge_Dev.pfx"
$SourceIcon    = Join-Path $ProjectRoot "assets\icons\app.png"

# ── Find Windows SDK tools ──────────────────────────────────────────────────
function Find-SdkTool {
    param([string]$ToolName)
    
    $sdkPaths = @(
        "${env:ProgramFiles(x86)}\Windows Kits\10\bin",
        "$env:ProgramFiles\Windows Kits\10\bin"
    )
    
    foreach ($sdkPath in $sdkPaths) {
        if (Test-Path $sdkPath) {
            $tool = Get-ChildItem -Path $sdkPath -Recurse -Filter "$ToolName.exe" -ErrorAction SilentlyContinue |
                    Sort-Object { $_.Directory.Name } -Descending |
                    Select-Object -First 1
            if ($tool) { return $tool.FullName }
        }
    }
    
    # Try PATH
    $inPath = Get-Command $ToolName -ErrorAction SilentlyContinue
    if ($inPath) { return $inPath.Source }
    
    return $null
}

$MakeAppx = Find-SdkTool "makeappx"
$SignTool = Find-SdkTool "signtool"

if (-not $MakeAppx) {
    Write-Error @"
makeappx.exe not found. Please install the Windows 10 SDK:
  https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/
Or install via Visual Studio Installer -> Individual Components -> 'Windows 10 SDK'
"@
    exit 1
}

Write-Host "Found makeappx: $MakeAppx" -ForegroundColor Green
if ($SignTool) {
    Write-Host "Found signtool: $SignTool" -ForegroundColor Green
} else {
    Write-Warning "signtool.exe not found. Signing will be skipped."
    $SkipSign = $true
}

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1: Build PyInstaller executable
# ══════════════════════════════════════════════════════════════════════════════
if (-not $SkipBuild) {
    Write-Host "`n═══ Step 1: Building PyInstaller executable ═══" -ForegroundColor Cyan
    
    Push-Location $ProjectRoot
    try {
        if (Test-Path "DocForge.spec") {
            & pyinstaller DocForge.spec --noconfirm
        } else {
            & pyinstaller main.py --name DocForge --windowed --icon "assets\icons\app.ico" `
                --add-data "assets;assets" --noconfirm
        }
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error "PyInstaller build failed with exit code $LASTEXITCODE"
            exit 1
        }
    } finally {
        Pop-Location
    }
    
    if (-not (Test-Path (Join-Path $DistDir "DocForge.exe"))) {
        Write-Error "Build output not found at: $DistDir\DocForge.exe"
        exit 1
    }
    Write-Host "PyInstaller build complete." -ForegroundColor Green
} else {
    Write-Host "`n═══ Step 1: Skipping PyInstaller build (using existing dist\) ═══" -ForegroundColor Yellow
    if (-not (Test-Path $DistDir)) {
        Write-Error "dist\DocForge directory not found. Run without -SkipBuild first."
        exit 1
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2: Generate MSIX logo assets
# ══════════════════════════════════════════════════════════════════════════════
Write-Host "`n═══ Step 2: Generating MSIX logo assets ═══" -ForegroundColor Cyan

# Create output directories (clean PackageLayout to avoid stale/locked files)
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
if (Test-Path $PackageLayout) {
    Remove-Item -Path $PackageLayout -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Force -Path $PackageLayout | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $PackageLayout "Assets") | Out-Null

# Asset size requirements for MSIX
$assetSpecs = @(
    @{ Name = "Square44x44Logo.png";   Width = 44;  Height = 44  },
    @{ Name = "Square150x150Logo.png"; Width = 150; Height = 150 },
    @{ Name = "Wide310x150Logo.png";   Width = 310; Height = 150 },
    @{ Name = "LargeTile.png";         Width = 310; Height = 310 },
    @{ Name = "StoreLogo.png";         Width = 50;  Height = 50  },
    @{ Name = "SplashScreen.png";      Width = 620; Height = 300 }
)

# Check if we have pre-made assets in msix/Assets
$prebuiltAssets = Test-Path $MsixAssetsDir
if ($prebuiltAssets) {
    $allExist = $true
    foreach ($spec in $assetSpecs) {
        if (-not (Test-Path (Join-Path $MsixAssetsDir $spec.Name))) {
            $allExist = $false
            break
        }
    }
    if ($allExist) {
        Write-Host "Using pre-built assets from msix\Assets\" -ForegroundColor Green
        Copy-Item -Path "$MsixAssetsDir\*" -Destination (Join-Path $PackageLayout "Assets") -Force
    } else {
        $prebuiltAssets = $false
    }
}

if (-not $prebuiltAssets) {
    Write-Host "Generating assets from source icon..." -ForegroundColor Yellow
    
    if (-not (Test-Path $SourceIcon)) {
        Write-Error "Source icon not found: $SourceIcon. Please place app.png in assets\icons\"
        exit 1
    }
    
    # Use .NET System.Drawing to resize images
    Add-Type -AssemblyName System.Drawing
    
    $sourceImage = [System.Drawing.Image]::FromFile($SourceIcon)
    
    foreach ($spec in $assetSpecs) {
        $destPath = Join-Path (Join-Path $PackageLayout "Assets") $spec.Name
        $destBitmap = New-Object System.Drawing.Bitmap($spec.Width, $spec.Height)
        $graphics = [System.Drawing.Graphics]::FromImage($destBitmap)
        $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
        $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
        $graphics.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
        
        # For non-square assets (Wide tile, Splash), center the icon
        if ($spec.Width -ne $spec.Height) {
            $graphics.Clear([System.Drawing.Color]::Transparent)
            $iconSize = [Math]::Min($spec.Width, $spec.Height) * 0.7
            $x = ($spec.Width - $iconSize) / 2
            $y = ($spec.Height - $iconSize) / 2
            $graphics.DrawImage($sourceImage, $x, $y, $iconSize, $iconSize)
        } else {
            $graphics.DrawImage($sourceImage, 0, 0, $spec.Width, $spec.Height)
        }
        
        $destBitmap.Save($destPath, [System.Drawing.Imaging.ImageFormat]::Png)
        $graphics.Dispose()
        $destBitmap.Dispose()
        
        Write-Host "  Created: $($spec.Name) ($($spec.Width)x$($spec.Height))" -ForegroundColor DarkGreen
    }
    
    $sourceImage.Dispose()
    
    # Also copy generated assets back to msix/Assets for future builds
    New-Item -ItemType Directory -Force -Path $MsixAssetsDir | Out-Null
    Copy-Item -Path (Join-Path $PackageLayout "Assets\*") -Destination $MsixAssetsDir -Force
}

Write-Host "Assets ready." -ForegroundColor Green

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3: Assemble MSIX package layout
# ══════════════════════════════════════════════════════════════════════════════
Write-Host "`n═══ Step 3: Assembling MSIX package layout ═══" -ForegroundColor Cyan

# Copy all PyInstaller output to the package layout
# Using robocopy instead of Copy-Item to handle long file paths
Write-Host "  Copying application files from dist\DocForge\..." -ForegroundColor DarkGreen
& robocopy $DistDir $PackageLayout /E /NFL /NDL /NJH /NJS /NP /NS /NC
# robocopy returns 0-7 for success, 8+ for errors
if ($LASTEXITCODE -ge 8) {
    Write-Error "robocopy failed with exit code $LASTEXITCODE"
    exit 1
}
$LASTEXITCODE = 0  # Reset since robocopy uses non-zero for success

# Fix OPC naming conflicts between python-docx templates and MSIX packaging.
# MSIX uses OPC (Open Packaging Conventions) format internally, which reserves:
#   - [Content_Types].xml
#   - _rels/ directories and .rels files
# python-docx's extracted template contains these, causing makeappx to fail.
# Solution: Re-compress the template back into a .docx zip file.
$docxTemplateDir = Join-Path $PackageLayout "_internal\docx\templates\default-docx-template"
if (Test-Path $docxTemplateDir) {
    Write-Host "  Fixing OPC conflict: re-compressing docx template..." -ForegroundColor Yellow
    
    # First, restore the original [Content_Types].xml name if it was renamed
    $renamedCT = Join-Path $docxTemplateDir "_Content_Types_.xml"
    $originalCT = Join-Path $docxTemplateDir "[Content_Types].xml"
    if (Test-Path $renamedCT) {
        # Use cmd.exe to rename since PowerShell has issues with brackets
        & cmd /c "rename `"$renamedCT`" `"[Content_Types].xml`""
    }
    
    # Compress the template directory into a .docx file (which is a zip)
    # Compress-Archive only supports .zip extension, so create as .zip then rename
    $templatesDir = Join-Path $PackageLayout "_internal\docx\templates"
    $zipFile = Join-Path $templatesDir "default.zip"
    $docxFile = Join-Path $templatesDir "default.docx"
    if (Test-Path $zipFile) { Remove-Item $zipFile -Force }
    if (Test-Path $docxFile) { Remove-Item $docxFile -Force }
    
    # Create zip from the template directory contents
    Compress-Archive -LiteralPath (Get-ChildItem -LiteralPath $docxTemplateDir).FullName `
        -DestinationPath $zipFile -CompressionLevel Optimal
    
    # Rename .zip to .docx
    Rename-Item -LiteralPath $zipFile -NewName "default.docx" -Force
    
    # Remove the extracted template directory
    & cmd /c "rmdir /s /q `"$docxTemplateDir`""
    Write-Host "  Template re-compressed to default.docx" -ForegroundColor DarkGreen
} else {
    # Fallback: just rename any remaining [Content_Types].xml files
    $conflictFiles = Get-ChildItem -LiteralPath $PackageLayout -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -eq '[Content_Types].xml' }
    foreach ($f in $conflictFiles) {
        Rename-Item -LiteralPath $f.FullName -NewName '_Content_Types_.xml' -Force
        Write-Host "  Renamed conflicting file: $($f.FullName)" -ForegroundColor Yellow
    }
}

# Copy and update the manifest
$manifestSource = Join-Path $MsixSourceDir "AppxManifest.xml"
$manifestDest = Join-Path $PackageLayout "AppxManifest.xml"

if (Test-Path $manifestSource) {
    $manifestContent = Get-Content $manifestSource -Raw
    
    # Update version and publisher in the Identity element only (not the XML declaration)
    $manifestContent = $manifestContent -replace '(<Identity\s[^>]*?)Version="[^"]*"', "`$1Version=`"$Version`""
    $manifestContent = $manifestContent -replace '(<Identity\s[^>]*?)Publisher="[^"]*"', "`$1Publisher=`"$Publisher`""
    
    # Write UTF-8 without BOM (Set-Content -Encoding UTF8 adds BOM which makeappx rejects)
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($manifestDest, $manifestContent, $utf8NoBom)
    Write-Host "  Manifest copied and updated." -ForegroundColor DarkGreen
} else {
    Write-Error "AppxManifest.xml not found in msix\. Please run this script from the project root."
    exit 1
}

Write-Host "Package layout assembled at: $PackageLayout" -ForegroundColor Green

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4: Create MSIX package
# ══════════════════════════════════════════════════════════════════════════════
Write-Host "`n═══ Step 4: Creating MSIX package ═══" -ForegroundColor Cyan

if (Test-Path $MsixFile) {
    Remove-Item $MsixFile -Force
}

& $MakeAppx pack /d $PackageLayout /p $MsixFile /o

if ($LASTEXITCODE -ne 0) {
    Write-Error "makeappx.exe failed with exit code $LASTEXITCODE"
    exit 1
}

Write-Host "MSIX package created: $MsixFile" -ForegroundColor Green

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5: Sign the MSIX package (for sideloading/testing)
# ══════════════════════════════════════════════════════════════════════════════
if (-not $SkipSign) {
    Write-Host "`n═══ Step 5: Signing MSIX package ═══" -ForegroundColor Cyan
    
    # Create a self-signed certificate for development
    if (-not (Test-Path $CertFile)) {
        Write-Host "  Creating self-signed certificate..." -ForegroundColor Yellow
        
        $cert = New-SelfSignedCertificate `
            -Type Custom `
            -Subject $Publisher `
            -KeyUsage DigitalSignature `
            -FriendlyName "DocForge Dev Certificate" `
            -CertStoreLocation "Cert:\CurrentUser\My" `
            -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")
        
        $securePassword = ConvertTo-SecureString -String $CertificatePassword -Force -AsPlainText
        Export-PfxCertificate -Cert $cert -FilePath $CertFile -Password $securePassword | Out-Null
        
        Write-Host "  Certificate created: $CertFile" -ForegroundColor DarkGreen
        Write-Host "  Certificate thumbprint: $($cert.Thumbprint)" -ForegroundColor DarkGreen
        
        # Also export .cer for installing on test machines
        $cerFile = Join-Path $OutputDir "DocForge_Dev.cer"
        Export-Certificate -Cert $cert -FilePath $cerFile | Out-Null
        Write-Host "  Public certificate: $cerFile" -ForegroundColor DarkGreen
    } else {
        Write-Host "  Using existing certificate: $CertFile" -ForegroundColor Yellow
    }
    
    # Sign the MSIX
    $securePassword = ConvertTo-SecureString -String $CertificatePassword -Force -AsPlainText
    & $SignTool sign /fd SHA256 /a /f $CertFile /p $CertificatePassword $MsixFile
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "signtool.exe failed with exit code $LASTEXITCODE"
        exit 1
    }
    
    Write-Host "MSIX package signed successfully." -ForegroundColor Green
} else {
    Write-Host "`n═══ Step 5: Skipping signing (use -SkipSign:$false to enable) ═══" -ForegroundColor Yellow
    Write-Host "  Note: For Microsoft Store submission, Microsoft signs the package." -ForegroundColor Yellow
    Write-Host "  For sideloading, re-run without -SkipSign." -ForegroundColor Yellow
}

# ══════════════════════════════════════════════════════════════════════════════
# DONE
# ══════════════════════════════════════════════════════════════════════════════
Write-Host "`n" -NoNewline
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  MSIX Build Complete!" -ForegroundColor Green
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "  Package:  $MsixFile" -ForegroundColor White
Write-Host "  Size:     $([math]::Round((Get-Item $MsixFile).Length / 1MB, 2)) MB" -ForegroundColor White
Write-Host ""

if (-not $SkipSign) {
    Write-Host "  To install for testing (sideloading):" -ForegroundColor Yellow
    Write-Host "    1. Install the certificate: $OutputDir\DocForge_Dev.cer" -ForegroundColor Gray
    Write-Host "       (Right-click -> Install -> Local Machine -> Trusted People)" -ForegroundColor Gray
    Write-Host "    2. Double-click the .msix file to install" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "  To submit to Microsoft Store:" -ForegroundColor Yellow
Write-Host "    1. Go to https://partner.microsoft.com" -ForegroundColor Gray
Write-Host "    2. Create a new app submission" -ForegroundColor Gray
Write-Host "    3. Upload: $MsixFile" -ForegroundColor Gray
Write-Host "    4. See store_submission.md for detailed instructions" -ForegroundColor Gray
Write-Host ""
