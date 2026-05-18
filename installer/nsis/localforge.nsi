; LocalForge NSIS installer (v1.1.0 — DirectML images + optional ZLUDA video).
;
; The image backend (DirectML) is bootstrapped at install time so the app
; can generate images immediately after first launch. The Video Pro backend
; (ZLUDA + CUDA-built PyTorch) is **opt-in** and installed on-demand from
; inside the app's Video Pro tab — it's a ~6 GB download and most users
; never need it, so we don't force it on everyone.

!define PRODUCT_NAME      "LocalForge"
!define PRODUCT_VERSION   "1.1.0"
!define PRODUCT_PUBLISHER "LocalForge"
!define PRODUCT_WEB_SITE  "https://localforge.ai"
!define UNINST_KEY        "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"

SetCompressor /SOLID lzma
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "LocalForge-Setup-${PRODUCT_VERSION}.exe"
InstallDir "$PROGRAMFILES64\LocalForge"
InstallDirRegKey HKLM "Software\${PRODUCT_NAME}" "Install_Dir"
RequestExecutionLevel admin
ShowInstDetails show
ShowUninstDetails show

!include "MUI2.nsh"
!define MUI_ICON   "..\..\src-tauri\icons\icon.ico"
!define MUI_UNICON "..\..\src-tauri\icons\icon.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "..\..\resources\installer_header.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "..\..\resources\installer_side.bmp"

!define MUI_WELCOMEPAGE_TITLE "Welcome to LocalForge ${PRODUCT_VERSION}"
!define MUI_WELCOMEPAGE_TEXT "LocalForge is a 100% offline AI image and video studio for Windows 11.$\r$\n$\r$\nThis installer will:$\r$\n  • Install the LocalForge app (Tauri desktop)$\r$\n  • Set up the image backend (DirectML, works on any GPU — tuned for AMD RX 7900 XT)$\r$\n  • Download SDXL Base + a starter model set (~7 GB)$\r$\n$\r$\nVideo Pro mode (ZLUDA + LTX-Video / Wan 2.1 / Hunyuan) is optional and can be installed later from inside the app with one click.$\r$\n$\r$\nNo cloud. No login. No telemetry."

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\..\LICENSE"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

!define MUI_FINISHPAGE_RUN "$INSTDIR\LocalForge.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch LocalForge"
!define MUI_FINISHPAGE_LINK "Open the Video Pro guide"
!define MUI_FINISHPAGE_LINK_LOCATION "https://github.com/localforge/localforge/blob/main/docs/VIDEO_PRO.md"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

; ----------------------------------------------------------------------------
; Sections
; ----------------------------------------------------------------------------

Section "LocalForge app (required)" SecMain
  SectionIn RO
  SetOutPath "$INSTDIR"
  File /r "..\..\src-tauri\target\release\bundle\nsis\*.exe"
  File /r "..\..\backend"
  File /r "..\..\resources"

  ; Start Menu + desktop shortcuts
  CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
  CreateShortcut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\LocalForge.exe"
  CreateShortcut "$SMPROGRAMS\${PRODUCT_NAME}\Open data folder.lnk" "$APPDATA\LocalForge"
  CreateShortcut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\LocalForge.exe"

  ; Uninstall registry
  WriteRegStr HKLM "${UNINST_KEY}" "DisplayName"     "${PRODUCT_NAME}"
  WriteRegStr HKLM "${UNINST_KEY}" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "${UNINST_KEY}" "DisplayVersion"  "${PRODUCT_VERSION}"
  WriteRegStr HKLM "${UNINST_KEY}" "Publisher"       "${PRODUCT_PUBLISHER}"
  WriteRegStr HKLM "${UNINST_KEY}" "DisplayIcon"     "$INSTDIR\LocalForge.exe"
  WriteRegStr HKLM "${UNINST_KEY}" "URLInfoAbout"    "${PRODUCT_WEB_SITE}"
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Image backend (DirectML) + starter models" SecImageBackend
  ; This is the core image generator. We download embeddable Python,
  ; ComfyUI, torch-directml, and SDXL Base. ~7 GB total, runs on any GPU.
  DetailPrint "Setting up the image backend (DirectML)…"
  DetailPrint "This downloads ~7 GB and may take 5-15 minutes depending on your connection."
  nsExec::ExecToLog 'powershell.exe -ExecutionPolicy Bypass -NoProfile -Command "$env:LOCALFORGE_DATA_DIR=$env:APPDATA + \"\\LocalForge\"; & \"$INSTDIR\\backend\\python\\python.exe\" \"$INSTDIR\\backend\\scripts\\bootstrap.py\""'
  Pop $0
  ${If} $0 != 0
    DetailPrint "Bootstrap exited with code $0 — you can re-run it from the app's Settings page."
  ${EndIf}
SectionEnd

Section /o "Video Pro backend (ZLUDA, ~6 GB, optional)" SecVideoPro
  ; Most users skip this here and install on-demand from the app's
  ; Video Pro tab, which provides a nicer progress UI with live logs.
  ; Selecting it here just kicks off the same installer script up front.
  DetailPrint "Installing Video Pro backend (ZLUDA + CUDA-built PyTorch)…"
  DetailPrint "This downloads ~6 GB. You can also install this later from the app."
  nsExec::ExecToLog 'powershell.exe -ExecutionPolicy Bypass -NoProfile -Command "$env:LOCALFORGE_DATA_DIR=$env:APPDATA + \"\\LocalForge\"; & \"$INSTDIR\\backend\\python\\python.exe\" \"$INSTDIR\\backend\\scripts\\install_video_pro.py\""'
  Pop $0
  ${If} $0 != 0
    DetailPrint "Video Pro setup exited with code $0 — open the Video Pro tab in the app to retry."
  ${EndIf}
SectionEnd

; Component descriptions
LangString DESC_SecMain         ${LANG_ENGLISH} "Required. The LocalForge desktop app, backend manager, and built-in workflows."
LangString DESC_SecImageBackend ${LANG_ENGLISH} "Recommended. DirectML-based image generation. Works on any modern GPU; tuned for AMD RX 7900 XT. Downloads ~7 GB including SDXL Base."
LangString DESC_SecVideoPro     ${LANG_ENGLISH} "Optional. Video Pro mode uses ZLUDA to run CUDA-only models (LTX-Video, Wan 2.1, Hunyuan) on AMD GPUs. ~6 GB. You can also install this later from inside the app."

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecMain}         $(DESC_SecMain)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecImageBackend} $(DESC_SecImageBackend)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecVideoPro}     $(DESC_SecVideoPro)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; ----------------------------------------------------------------------------
; Uninstall
; ----------------------------------------------------------------------------

Section "Uninstall"
  Delete "$DESKTOP\${PRODUCT_NAME}.lnk"
  RMDir /r "$SMPROGRAMS\${PRODUCT_NAME}"
  RMDir /r "$INSTDIR"
  DeleteRegKey HKLM "${UNINST_KEY}"
  DeleteRegKey HKLM "Software\${PRODUCT_NAME}"
  ; Note: user data in %APPDATA%\LocalForge (models, outputs, settings)
  ; is preserved by default. Delete it manually if you want a full wipe.
SectionEnd
