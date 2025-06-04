pyinstaller --clean --noconfirm build-dir.spec
PowerShell -Command Compress-Archive -Path dist\ConeDetectionML\* -DestinationPath dist\ConeDetectionML-1.2.0-win64.zip -Force
