pyinstaller --clean build-app-dir.spec
rm -rf dist/ConeDetectionML/
hdiutil create "ConeDetectionML-Darwin.dmg" -ov -volname "ConeDetectionML" -fs HFS+ -srcfolder "dist/"
