# In-Depth Tutorial: Using Camera Module 3 on Raspberry Pi

This tutorial provides a comprehensive guide on how to take a photo using a Raspberry Pi Camera Module 3 with a modern Raspberry Pi running the latest Raspberry Pi OS. It covers the command-line and Python methods.

While this guide was requested for a "Compute Module 5," that module is not yet released. The instructions here are for any modern Raspberry Pi (Pi 4, Pi 5, CM4) running a recent version of Raspberry Pi OS (Bullseye or newer) and will be applicable when the CM5 is released.

---

## 1. Prerequisites

### Hardware
*   **Raspberry Pi:** Any recent model (Pi 4, Pi 5, Compute Module 4, etc.).
*   **Camera Module 3:** Or any other Raspberry Pi compatible camera.
*   **Carrier Board:** If using a Compute Module, you need a carrier board with a camera (CSI) connector.
*   **Power Supply:** A suitable power supply for your Raspberry Pi.
*   **SD Card:** With a fresh installation of Raspberry Pi OS (Bullseye or newer).

### Software
*   **Raspberry Pi OS:** Bullseye or newer. These versions use the modern `libcamera` stack.
*   **Terminal Access:** Either directly with a monitor and keyboard or via SSH.

---

## 2. Hardware Setup

1.  **Power Down:** Ensure your Raspberry Pi is completely powered off and disconnected from the power supply.
2.  **Connect the Camera:**
    *   Locate the Camera Serial Interface (CSI) port on your Raspberry Pi or Compute Module carrier board. It's a long, thin connector, usually plastic.
    *   Gently pull up the tabs on the edges of the port.
    *   Take the camera's ribbon cable. The blue strip on the cable should face away from the circuit board on a standard Pi (towards the USB/Ethernet ports). On a carrier board, consult its documentation, but typically the exposed metal contacts go towards the contacts in the connector.
    *   Insert the ribbon cable squarely into the connector.
    *   Push the tabs back down to secure the cable.
3.  **Power Up:** Reconnect the power supply and boot your Raspberry Pi.

---

## 3. Software Configuration

You must enable the camera interface before the OS will recognize it.

1.  **Open Terminal:** Access your Raspberry Pi's command line.
2.  **Run Configuration Tool:**
    ```bash
    sudo raspi-config
    ```
3.  **Navigate to Camera:** Use the arrow keys to select `3 Interface Options` and press Enter.
4.  **Enable Camera:** Select `I1 Legacy Camera` and, when prompted, select `<No>` to **disable** the legacy stack. Then, back in the `Interface Options` menu, select `I1 Camera` and select `<Yes>` to **enable** the modern `libcamera` interface.
5.  **Finish and Reboot:** Navigate to `<Finish>` in the main menu. It will ask if you want to reboot. Select `<Yes>`.

---

## 4. Taking a Photo (Command-Line)

The modern tool for taking photos from the command line is `rpicam-still`.

### Basic Photo
This is the simplest command. It will show a 5-second preview on the connected display and then save the image.

```bash
rpicam-still -o test_image.jpg
```
*   `-o`: Specifies the **o**utput filename.

### Taking a Photo Without a Preview
Useful for scripts or SSH sessions where you don't have a display.

```bash
rpicam-still -o no_preview.jpg --nopreview
```
*   `--nopreview`: Skips the live preview window.

### Common `rpicam-still` Options

*   **Set Resolution:**
    ```bash
    rpicam-still -o high_res.jpg --width 1920 --height 1080
    ```
*   **Set a Delay:** Wait for a few seconds before taking the picture. The value is in milliseconds.
    ```bash
    rpicam-still -o delayed.jpg --timeout 3000
    ```
    *(This waits 3 seconds before capturing)*

*   **Change Image Format (e.g., PNG):**
    ```bash
    rpicam-still -o image.png -e png
    ```
    *   `-e`: Specifies the **e**ncoding.

*   **Timelapse:** Take a picture every few seconds for a total duration.
    ```bash
    # Take a picture every 10 seconds for 1 minute
    rpicam-still --timelapse 10000 -t 60000 -o timelapse_%04d.jpg
    ```
    *   `--timelapse`: Interval between shots in milliseconds.
    *   `-t`: Total **t**imeout for the entire process in milliseconds.
    *   `%04d`: A special formatter that names files `timelapse_0001.jpg`, `timelapse_0002.jpg`, etc.

---

## 5. Taking a Photo (Python)

For more control and integration into applications, use the `picamera2` library. It should be pre-installed on recent Pi OS versions. If not, install it with `sudo apt install python3-picamera2`.

### Simple Python Script

Create a file named `take_photo.py`:

```python
# take_photo.py
from picamera2 import Picamera2
import time

# 1. Initialize the camera
print("Initializing camera...")
picam2 = Picamera2()

# 2. Create a configuration for a still image
#    You can customize this, e.g., main={"size": (1920, 1080)}
config = picam2.create_still_configuration()
picam2.configure(config)

# 3. Start the camera system
print("Starting camera...")
picam2.start()

# 4. Give the camera time to adjust to light levels
#    This is important to avoid dark or poorly exposed images.
time.sleep(2)

# 5. Capture the image and save it
output_filename = "python_photo.jpg"
print(f"Capturing image to {output_filename}...")
picam2.capture_file(output_filename)

# 6. Stop the camera
picam2.stop()
print("Done. Camera stopped.")

```

### How to Run the Script

1.  Save the code above into a file named `take_photo.py`.
2.  Run it from the terminal:
    ```bash
    python3 take_photo.py
    ```
3.  A new file, `python_photo.jpg`, will be created in the same directory.

---

## 6. Troubleshooting

*   **"Camera not detected":**
    *   Double-check the ribbon cable connection. It's the most common point of failure. Ensure it's seated correctly and the metal contacts are facing the right way.
    *   Make sure you enabled the camera in `raspi-config` and rebooted.
    *   Ensure you are using the modern `libcamera` interface, not the legacy one.

*   **"Command not found: rpicam-still":**
    *   Your Raspberry Pi OS might be too old. Upgrade to Bullseye or a newer version.

*   **Python script fails with `ModuleNotFoundError: No module named 'picamera2'`:**
    *   Install the library using the command: `sudo apt update && sudo apt install python3-picamera2`.
