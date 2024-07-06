### Arnergy EMS Flasher Prototype

### Setup
### Requirements 
- Python 3.x 

### Clone the Repository 
```bash
$ git clone "https://github.com/rexsimiloluwah/arnergy-ems-flasher-prototype"
$ cd arnergy-ems-flasher-prototype
```
### File structure 
- `assets` - Contains images and icons used in the app
- `app.py` - Contains the main app interface and logic in PyQt5
- `config.json` - Basic app configuration
- `dfu.py` - USB DFU 1.1 protocol spec implementation (https://github.com/vpelletier/python-dfu)
- `serial_test.py` - For testing pyserial 
- `utils.py` - Backend for fetching device data from the solarbase setup API

### Create a Virtual environment 
For windows: 
```bash
$ python -m venv env
$ source env/Scripts/activate
```
For Linux-based OS:
```bash
$ python3 -m venv env
$ source env/bin/activate
```
### Install dependencies 
```bash
$ pip install -r requirements.txt
```
### Run the App 
```bash
$ python app.py
```

### To bundle the app 
Pyinstaller can be used to bundle the application :-

```bash
$ pip install pyinstaller 
```

```bash
$ pyinstaller app.py --hiddenimport pyserial --add-data "assets;./assets" --add-data "components;./components" --add-data "utils.py;." --add-data "config.json;." --add-data "dfu.py;." --add-data "guide.html;." --onefile --name EMS_Flasher --icon arnergy-icon.ico --windowed
``` 

`windowed converts it to GUI only, no console`
