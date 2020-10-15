# 3D-PLI-Demo

## install

### unix

``` sh
python3 -m venv env
source env/bin/activate
pip install pip --upgrade
pip install -r requirements.txt
python3 main.py
```

### windows

``` sh
python3 -m venv env
.\env\Scripts\activate
pip install pip --upgrade
pip install -r requirements.txt
python3 main.py
```

## TODO

### BUGS

- clean menu entries before adding after port camera change

### Improvements

- improve 3d rendering
  - opengl: rotatable filters
  - opengl: RFC shaders
  - resize event rendering
- improve pli mask
- only live view mode
- crop image top and bottom
- visual feedback when resetting / calculating
- zoomable central image?
- right click mouse on image functions?
- check qt camera viewfinder again
