Name "Gradient Data Uploader Installer"
OutFile "gdu.exe"

Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

Icon grd.ico
InstallDir "$PROGRAMFILES\Gradient Data Uploader"
DirText "This will install the Gradient Data Uploader on your computer."

Section ""
  SetOutPath $INSTDIR
  File /r dist\*.*
  WriteUninstaller $INSTDIR\Uninstall.exe
  CreateDirectory "$SMPROGRAMS\Gradient Data Uploader"
  CreateShortCut "$SMPROGRAMS\Gradient Data Uploader\Gradient Data Uploader.lnk" "$INSTDIR\gdu.exe"
  CreateShortCut "$SMPROGRAMS\Gradient Data Uploader\Uninstall.lnk" "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
  Delete $INSTDIR\Uninst.exe
  RMDir /r /REBOOTOK $INSTDIR
SectionEnd
