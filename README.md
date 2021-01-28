# True-Randomness
This code was made for Delta X basketball competition

# Modules
Before code execution make sure these modules are installed:
  - datetime
  - enum
  - websocket
  - simple_pid
  - pyrealsense2
  - pathlib
  - json
  - threading
  - math
  - struct
  - cv2
  - serial
  - numpy
  - configparser

# How to Run
Before main.py code running, make sure thresholds are correctly configured.

Run calibration.py and type what color to configre, and proceed with calibration.

After calibration, change in the file autoMov.py line:
```
conn = websocket.create_connection('ws://<IP>:<PORT>/')
```
Where is IP and PORT is the address of WebSocket server

Then change robotID in config.ini to your own

# Contributors
  - Kirill Anohin
  - Kristo Pool
  - Hans Pärtel Pani

If you wish to know more about how this project was made visit [True-Randomness_Wiki](https://digilabor.ut.ee/index.php/True_Randomness)
