pyinstaller --clean --noconfirm build-dir.spec
PowerShell -Command Compress-Archive -Path dist\ConeDetectionML\* -DestinationPath dist\ConeDetectionML-1.2.2-win64.zip -Force
