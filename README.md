# Cone Detection ML (Machine Learning Edition)
#### A software package for identifying cone photoreceptors in non-confocal adaptive optics images such as split detection, using pre-trained A-GAN machine learning model and manual editing. 

*Jianfei Liu (NEI/NIH), Andrei Volkov (NEI/NIH Contractor), and Johnny Tam (NEI/NIH), with research support from the Intramural Research Program of the National Institutes of Health.*

<img src="assets/app_main.png" width="563" height="360" />

---------------

## Setting up development environment

1. Download and install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/products/individual).

2. Check out **ConeDetectionML** to a local directory `<prefix>/ConeDetectionML`. (Replace `<prefix>` with any suitable local directory).

3. Run Anaconda Prompt (or Terminal), cd to `<prefix>/ConeDetectionML`.

4. Create Conda Virtual Environment (do this once, next time skip to the next step):

	`conda env create --file conda-environment-win.yml` (Windows)

	`conda env create --file conda-environment-mac.yml` (Mac OS)
   
5. Activate the Virtual Environment:

	`conda activate ConeDetection`
   
6. Start the application:

	`python __main__.py`
  
7. Build "frozen Python" application:

	`pyinstaller --clean --noconfirm build-dir.spec`

If successful, the result is the directory `ConeDetectionML` inside `<prefix>/ConeDetectionML/dist/`. You can copy this directory with all its contents to a different machine, and run the executable `__main__` (in MacOS and Linux) or `__main__.exe` (in Windows). It does not need Conda VEs or other development tools.

In MacOS systems, you can build a Mac application instead:

`pyinstaller --clean --noconfirm build-app-dir.spec`

The result is `<prefix>/ConeDetectionML/dist/ConeDetectionML.app`.

## Creating Windows installer using NSIS

1. Download and install [NSIS](https://nsis.sourceforge.io/Download) if you don't have it already.

2. Follow steps 1 through 7 of *Setting up development environment* to build the directory containing "frozen Python" application.

3. Open Command Prompt (or Conda Prompt), cd to `<prefix>/ConeDetectionML`.

4. Run NSIS:

`"C:\Program Files (x86)\NSIS\makensis.exe" /V4 build-win64-installer.nsi`

(Replace `C:\Program Files (x86)\NSIS` with the actual installation directory, if different from default).
If successful, the result is `<prefix>/ConeDetectionML/dist/ConeDetectionML-{version}-win64.exe`. This is a regular Windows installer, which can be distributed to other Windows systems. It requires admin access.

<img src="assets/wininstall.png" width="463" height="360" />

## Creating MAC OS installer (.dmg)

1. Make sure Xcode is installed (normally, via Apple App Store).

2. Follow steps 1 through 5 of *Setting up development environment* to setup the development environment.

3. At the Conda prompt with *ConeDetection* activated, cd to `<prefix>/ConeDetectionML` and type the command:

	`bash make_dmg.sh`

If prompted to allow Terminal to run Finder scripts, answer "Allow". The result is `<prefix>/ConeDetectionML/dist/ConeDetectionML-{version}-Darwin.dmg`. It is a Mac OS disk image file; when opened, it asks for accepting the license agreement, then mounts itself as an external drive and opens a Finder window, that looks like this:

<img src="assets/macinstall.png" width="605" height="360" />

You can run the app by double-clicking on the icon, or copy it to your Applications folder by dragging the icon over "Applications". Once ConeDetectionML is in your Applications folder, you can eject the *ConeDetectionML* disk, and delete `ConeDetectionML-{version}-Darwin.dmg`.

---------------

## Deleting Conda Virtual Environment

To delete the Virtual environment at the Conda prompt, deactivate it first if it is active:

`conda deactivate`

then type:

`conda remove --name ConeDetection`
   