VERSION="1.1.2"
rm -rf build/
rm -rf dist/
pyinstaller --clean --noconfirm build-app-dir.spec
rm -rf dist/ConeDetectionML/
hdiutil create "ConeDetectionML-Darwin0.dmg" -format UDRW -ov -volname "ConeDetectionML" -fs HFS+ -srcfolder "dist/" -attach
ln -s /Applications /Volumes/ConeDetectionML/Applications
mkdir /Volumes/ConeDetectionML/.background
cp MacOS/DMGbackground.tif /Volumes/ConeDetectionML/.background/background.tif
osascript MacOS/DMGSetup.scpt ConeDetectionML
hdiutil detach /Volumes/ConeDetectionML
#python MacOS/licenseDMG.py ConeDetectionML-Darwin0.dmg Help/License.txt
hdiutil convert ConeDetectionML-Darwin0.dmg -format UDZO -o "dist/ConeDetectionML-${VERSION}-Darwin.dmg"
rm ConeDetectionML-Darwin0.dmg
dmg-license MacOS/dmg-license-spec.json "dist/ConeDetectionML-${VERSION}-Darwin.dmg"
