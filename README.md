# 3D-PLI-Demo

## clone

git lfs for images and video files

```sh
git clone git@jugit.fz-juelich.de:inm-1/fa/3d-pli/general/pli-demo.git --single-branch
git lfs pull origin data/
```

## install

### unix

```sh
python3 -m venv env
source env/bin/activate
pip install pip --upgrade
pip install -r requirements.txt
python3 main.py
```

### windows

in power shell:

```sh
#mainwindow = MainWindow()
# mainwindow.resize(1600, 1600 // 1.618)
# mainwindow.show()
#mainwindow.showMaximized()
#app.exec_()

controller.show_offset()
.\run_windows.ps1
```

or

```sh
python.exe -m venv env
.\env\Scripts\activate
pip.exe install pip --upgrade
pip.exe install -r requirements.txt
python.exe main.py
```

#### exe

```
pyinstaller .\main.py --onefile
```

## TODO

### BUGS

### Improvements

- improve 3d rendering
- improve pli mask
- only live view mode
- visual feedback when resetting / calculating
- zoomable central image?
- right click mouse on image functions?
- check qt camera viewfinder again
