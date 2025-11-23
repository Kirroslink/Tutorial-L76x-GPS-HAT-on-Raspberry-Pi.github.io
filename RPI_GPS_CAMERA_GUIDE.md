# Guide: GPS-Triggered Camera on Raspberry Pi

This guide explains how to set up your Raspberry Pi to take a photo that is precisely synchronized with a GPS time pulse (PPS), and then embed the GPS coordinates into the photo's EXIF data.

---

### Part 1: Hardware Setup

You will need a Raspberry Pi, a Pi Camera Module, and a GPS module that has a PPS (or 1PPS) output pin.

1.  **Connect the Pi Camera:**
    *   Connect the camera ribbon cable to the CSI port on your Raspberry Pi. Ensure the blue tab on the cable faces the Ethernet/USB ports.

2.  **Connect the GPS Module:**
    *   **Power:** Connect the GPS module's `VCC` to a 3.3V pin on the Pi and `GND` to a Ground pin.
    *   **Serial (UART):** This is for reading the GPS location data (NMEA sentences).
        *   Connect the GPS `TX` (Transmit) pin to the Pi's `RX` (Receive) pin (GPIO 15).
        *   Connect the GPS `RX` (Receive) pin to the Pi's `TX` (Transmit) pin (GPIO 14).
    *   **PPS Signal:** This is for the high-precision timing trigger.
        *   Connect the GPS module's `PPS` output pin to **GPIO 17** on the Raspberry Pi.

**Pinout Summary (Physical Pins on Pi Header):**

| GPS Pin | Pi Pin (Physical) | Pi Pin (BCM) | Purpose                  |
|---------|-------------------|--------------|--------------------------|
| VCC     | 1 (3.3V Power)    | -            | Power for GPS            |
| GND     | 6 (Ground)        | -            | Common Ground            |
| TX      | 10 (GPIO 15)      | GPIO 15      | GPS data to Pi (RXD)     |
| RX      | 8 (GPIO 14)       | GPIO 14      | Pi commands to GPS (TXD) |
| PPS     | 11 (GPIO 17)      | **GPIO 17**      | 1 pulse-per-second signal|

---

### Part 2: Software & Dependencies

Before running the script, you need to configure the Raspberry Pi and install the necessary Python libraries.

1.  **Enable Pi Interfaces:**
    *   Open the configuration tool in your terminal:
        ```bash
        sudo raspi-config
        ```
    *   Navigate to **Interface Options**.
    *   Enable **I1 Legacy Camera**.
    *   Enable **I5 Serial Port**.
        *   When asked "Would you like a login shell to be accessible over serial?", select **NO**.
        *   When asked "Would you like the serial port hardware to be enabled?", select **YES**.
    *   Finish and reboot if prompted.

2.  **Install System and Python Libraries:**
    *   Open a terminal and run the following commands to install everything needed. The `picamera2` and `gpiod` libraries are best installed from the system's package manager on recent versions of Pi OS.

    ```bash
    # Update your package list
    sudo apt update

    # Install system libraries for camera and GPIO
    sudo apt install -y python3-picamera2 python3-gpiod

    # Install Python libraries using pip for serial data, NMEA parsing, and EXIF handling
    pip install pyserial pynmea2 piexif
    ```

---

### Part 3: The Python Script

The script `capture_with_gps.py` has been created for you. Here is a brief explanation of how it works:

*   **Multithreading:** It starts a background thread that *only* listens for and parses GPS data from the serial port. This prevents the main part of the program from getting stuck waiting for serial data.
*   **PPS Trigger:** The main thread monitors GPIO 17. When the GPS module gets a satellite lock, it sends out a very sharp electrical pulse once per second on the PPS pin. The script detects the "rising edge" of this pulse.
*   **Capture & EXIF:** As soon as the pulse is detected, the script tells the camera to take a picture. It then grabs the most recent GPS data collected by the background thread, formats it correctly, and injects it into the JPEG's EXIF metadata before saving the file.
*   **Configuration:** You can easily change the GPIO pin, serial port, or output directory at the top of the script. **Note:** The script is set for a Raspberry Pi 5 (`gpiochip4`). If you use a Pi 4 or older, you must change `Chip('gpiochip4')` to `Chip('gpiochip0')`.

---

### Part 4: How to Run the Script

1.  **Get a GPS Fix:** Take your Raspberry Pi somewhere with a clear view of the sky. The GPS module's indicator light should start blinking, signifying it has a satellite lock. This can take a few minutes.

2.  **Check for GPS Data (Optional):** You can "listen" to the serial port to see the raw NMEA data from the GPS module:
    ```bash
    cat /dev/ttyS0
    ```
    You should see lines starting with `$GPRMC`, `$GPGGA`, etc. Press `Ctrl+C` to stop.

3.  **Run the Python Script:**
    *   Navigate to the directory where the script is saved.
    *   Execute it:
        ```bash
        python capture_with_gps.py
        ```

4.  **Output:**
    *   The script will first wait for a valid GPS fix from the background thread.
    *   Once it has a fix, it will print "Monitoring GPIO pin...".
    *   Each time a PPS pulse is received (once per second), it will take a photo and save it to the `gps_photos` directory.
    *   Press `Ctrl+C` to stop the script gracefully.

You can then view the photos in the `gps_photos` folder and check their properties/details to see the embedded GPS coordinates.
