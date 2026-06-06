[Setup]
AppId={{DocForge}
AppName=DocForge
AppVersion=1.0.0
AppPublisher=Thirumal Dhakshnamoorthy
AppPublisherURL=https://github.com/
DefaultDirName={pf}\DocForge
DefaultGroupName=DocForge
OutputDir=installer_output
OutputBaseFilename=DocForge_Setup_v1.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=assets\icons\app.ico
UninstallDisplayIcon={app}\DocForge.exe

[Files]
Source: "dist\DocForge\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\DocForge"; Filename: "{app}\DocForge.exe"
Name: "{autodesktop}\DocForge"; Filename: "{app}\DocForge.exe"

[Run]
Filename: "{app}\DocForge.exe"; Description: "Launch DocForge"; Flags: nowait postinstall skipifsilent