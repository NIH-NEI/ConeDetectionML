
Packaging into single executable.

1. Download and install Miniconda (or Anaconda).
2. Run Anaconda Prompt, cd to directory '<...>/ConeDetectionML'.
3. Create virtual environment (do this once, next time skip to the next step):
   conda env create --file conda-environment.yml
NOTE that this environment is identical to ConeDetection; if you already created one
for ConeDetection, skip to the next step.
4. Activate virtual environment:
   conda activate ConeDetection
5. (optional step) Make sure the VE is good for running Python code directly:
   python __main__.py
6. Build the target executable:
   make_exe.bat
The resulting exe is: <...>/ConeDetectionML/dist/ConeDetectionML.exe

Building DMG for Mac:
   pyinstaller --clean build-app-dir.spec
   rm -rf dist/ConeDetectionML/
   hdiutil create "ConeDetectionML-Darwin.dmg" -ov -volname "ConeDetectionML" -fs HFS+ -srcfolder "dist/"

To delete the virtual environment, deactivate it first (if it is active):
   conda deactivate
Then type:
   conda env remove --name ConeDetection
