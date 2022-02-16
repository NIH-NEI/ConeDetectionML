rm -rf build/
rm -rf dist/
pyinstaller --clean --noconfirm build-app-dir.spec
rm -rf dist/ConeDetectionML/
hdiutil create "dist/ConeDetectionML-Darwin0.dmg" -format UDRW -ov -volname "ConeDetectionML" -fs HFS+ -srcfolder "dist/" -attach
ln -s /Applications /Volumes/ConeDetectionML/Applications
mkdir /Volumes/ConeDetectionML/.background
cp MacOS/DMGbackground.tif /Volumes/ConeDetectionML/.background/background.tif
osascript MacOS/DMGSetup.scpt ConeDetectionML
hdiutil detach /Volumes/ConeDetectionML
python MacOS/licenseDMG.py dist/ConeDetectionML-Darwin0.dmg Help/License.txt
rm dist/ConeDetectionML-1.1.0-Darwin.dmg
hdiutil convert dist/ConeDetectionML-Darwin0.dmg -format UDZO -o dist/ConeDetectionML-1.1.0-Darwin.dmg
rm dist/ConeDetectionML-Darwin0.dmg
