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

- improve pli mask
- plot widget: stop maximal resizing
- only live view mode
- sufficient brain segmentation
- right click mouse on image functions?
- crop image top and bottom
- visual feedback when resetting
- visual feedback instead of QLabel text?, at least improving
- visual feedback for captured angles
- rho = 0
- check qt camera viewfinder again
- improve 3d rendering
- resize event rendering
- opengl: rotatable filters
- opengl: RFC shaders
