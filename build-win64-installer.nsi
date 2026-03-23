
!define VERSION "1.2.1"
!define PATCH  "1"
!define INST_DIR "dist\ConeDetectionML"

Var START_MENU

!include "MUI2.nsh"

# set "Program Files" as install directory
InstallDir $PROGRAMFILES64\ConeDetectionML
 
;define installer name
Name "Cone Detection (ML) 1.2.1"
OutFile "dist\ConeDetectionML-1.2.1-win64.exe"

;SetCompressor lzma

!define MUI_HEADERIMAGE
!define MUI_ABORTWARNING

!define MUI_ICON Icons\ConeDetectionML256x256.ico
;!define MUI_UNICON Icons\ConeDetectionML256x256.ico

Function ConditionalAddToRegisty
  Pop $0
  Pop $1
  StrCmp "$0" "" ConditionalAddToRegisty_EmptyString
    WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\Cone Detection (ML)" \
    "$1" "$0"
    ;MessageBox MB_OK "Set Registry: '$1' to '$0'"
    DetailPrint "Set install registry entry: '$1' to '$0'"
  ConditionalAddToRegisty_EmptyString:
FunctionEnd

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "Help\License.txt"
!insertmacro MUI_PAGE_DIRECTORY

!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English" ;first language is the default language
 
# default section start
Section "-Core installation"

; Install for all users
SetShellVarContext all
 
# define output path
SetOutPath $INSTDIR
 
# specify file to go in output path
File /r dist\ConeDetectionML\*.*

WriteRegStr SHCTX "Software\National Eye Institute\Cone Detection (ML)" "" $INSTDIR
 
# define uninstaller name
WriteUninstaller $INSTDIR\uninstall.exe

Push "DisplayName"
Push "Cone Detection (ML)"
Call ConditionalAddToRegisty
Push "DisplayVersion"
Push "1.2.1"
Call ConditionalAddToRegisty
Push "Publisher"
Push "National Eye Institute"
Call ConditionalAddToRegisty
Push "UninstallString"
Push "$INSTDIR\uninstall.exe"
Call ConditionalAddToRegisty
Push "NoRepair"
Push "1"
Call ConditionalAddToRegisty
Push "DisplayIcon"
Push "$INSTDIR\__main__.exe,0"
Call ConditionalAddToRegisty
  
;Create shortcuts
CreateDirectory "$SMPROGRAMS\Cone Detection (ML)"
CreateShortCut "$SMPROGRAMS\Cone Detection (ML)\Cone Detection (ML).lnk" "$INSTDIR\__main__.exe"
CreateShortCut "$SMPROGRAMS\Cone Detection (ML)\Uninstall Cone Detection (ML).lnk" "$INSTDIR\uninstall.exe"
CreateShortCut "$DESKTOP\Cone Detection (ML).lnk" "$INSTDIR\__main__.exe"

; Write special uninstall registry entries
Push "StartMenu"
Push "Cone Detection (ML)"
Call ConditionalAddToRegisty

#-------
# default section end
SectionEnd
 
# create a section to define what the uninstaller does.
# the section will always be named "Uninstall"
Section "Uninstall"

; UnInstall for all users
SetShellVarContext all
 
ReadRegStr $START_MENU SHCTX \
   "Software\Microsoft\Windows\CurrentVersion\Uninstall\Cone Detection (ML)" "StartMenu"

 
# Always delete uninstaller first
Delete $INSTDIR\uninstall.exe
 
# now delete installed files
RMDir /r /REBOOTOK $INSTDIR

; Remove the registry entries.
DeleteRegKey SHCTX "Software\National Eye Institute\Cone Detection (ML)"
DeleteRegKey SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\Cone Detection (ML)"

Delete "$SMPROGRAMS\Cone Detection (ML)\Uninstall Cone Detection (ML).lnk"
Delete "$SMPROGRAMS\Cone Detection (ML)\Cone Detection (ML).lnk"
Delete "$DESKTOP\Cone Detection (ML).lnk"

DeleteRegKey /ifempty SHCTX "Software\National Eye Institute\Cone Detection (ML)"

SectionEnd

Function .onInit
  ReadRegStr $0 SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\Cone Detection (ML)" "UninstallString"
  StrCmp $0 "" inst

  MessageBox MB_YESNOCANCEL|MB_ICONEXCLAMATION \
  "Cone Detection (ML) is already installed. $\n$\nDo you want to uninstall the old version before installing the new one?" \
  /SD IDYES IDYES uninst IDNO inst
  Abort

;Run the uninstaller
uninst:
  ClearErrors
  StrLen $2 "\uninstall.exe"
  StrCpy $3 $0 -$2 # remove "\uninstall.exe" from UninstallString to get path
  ExecWait '"$0" /S _?=$3' ;Do not copy the uninstaller to a temp file

  IfErrors uninst_failed inst
uninst_failed:
  MessageBox MB_OK|MB_ICONSTOP "Uninstall failed."
  Abort

inst:
  ClearErrors

FunctionEnd

