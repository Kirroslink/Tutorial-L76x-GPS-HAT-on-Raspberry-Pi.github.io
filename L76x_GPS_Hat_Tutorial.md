# From Scratch Tutorial: L76x GPS HAT on Raspberry Pi

This tutorial provides a complete, beginner-friendly guide to setting up the Waveshare L76x GPS HAT on a modern Raspberry Pi (such as a Pi 4, Pi 5, or CM4/CM5). We will go from physical hardware setup to reading clean, usable GPS data with both the command line and a Python script.

---

## Part 1: Hardware Setup

1.  **Power Down:** Ensure your Raspberry Pi is completely powered off and unplugged.
2.  **Mount Battery (Optional):** If your HAT has a holder for an ML1220 rechargeable battery, installing one will help the GPS module achieve a faster "hot start" on subsequent power-ups.
3.  **Connect Antenna:** Screw the included GPS antenna onto the SMA connector on the HAT. For best results, the antenna needs a clear view of the sky. Place it near a window or outdoors.
4.  **Attach HAT to Pi:** Carefully align the 40-pin female header on the bottom of the GPS HAT with the 40 male GPIO pins on your Raspberry Pi. Press down firmly and evenly to seat the HAT securely.

---

## Part 2: OS Configuration (Enabling Serial UART)

The GPS module communicates with the Pi over a serial (UART) connection. You must enable this hardware interface.

1.  **Power Up:** Connect the power supply and boot your Raspberry Pi.
2.  **Open `raspi-config`:** Open a terminal window and run the configuration tool:
    ```bash
    sudo raspi-config
    ```
3.  **Navigate to Interface Options:** Use the arrow keys to select `3 Interface Options` and press Enter.
4.  **Select Serial Port:** Select `I6 Serial Port`.
5.  **Disable Serial Login Shell:** When asked, "Would you like a login shell to be accessible over serial?", select **`<No>`**. This is critical, as a login shell will conflict with the GPS data stream.
6.  **Enable Serial Hardware:** When asked, "Would you like the serial port hardware to be enabled?", select **`<Yes>`**.
7.  **Finish and Reboot:** Exit `raspi-config` by selecting `<Finish>`. If it asks you to reboot, select `<Yes>`.

Your Raspberry Pi's primary hardware UART is now enabled and available at `/dev/serial0`.

---

## Part 3: Initial Test (Reading Raw GPS Data)

Let's verify that the HAT is powered on and sending data. We'll use a simple tool called `minicom` to listen to the serial port.

1.  **Install `minicom`:**
    ```bash
    sudo apt update
    sudo apt install minicom -y
    ```
2.  **Listen to the Serial Port:** Run `minicom`, telling it to connect to `/dev/serial0` at a baud rate of 9600 (the default for the L76x).
    ```bash
    sudo minicom -D /dev/serial0 -b 9600
    ```
3.  **Check for NMEA Data:** You should see lines of text starting with `$` scrolling up the screen (e.g., `$GNRMC`, `$GNGGA`, etc.). This is the raw NMEA data from the GPS module. It might take a minute or two to get a satellite fix, especially on first use.

    If you see this data, your hardware is working correctly!

4.  **Exit `minicom`:** Press `Ctrl+A`, then `X`, then select `Yes` to exit.

---

## Part 4: Installing the GPS Daemon (`gpsd`)

Reading raw NMEA data is difficult. `gpsd` is a background service (daemon) that does the hard work for you. It listens to the raw data and provides a clean, simple interface for other programs to get GPS information.

1.  **Install `gpsd`:**
    ```bash
    sudo apt install gpsd gpsd-clients -y
    ```
2.  **Configure `gpsd`:** We need to tell `gpsd` which serial port to use.
    ```bash
    sudo nano /etc/default/gpsd
    ```
3.  **Edit the file** to look like this:
    ```
    # Default settings for gpsd.

    START_DAEMON="true"
    GPSD_OPTIONS="-n"
    DEVICES="/dev/serial0"
    USBAUTO="false"
    GPSD_SOCKET="/var/run/gpsd.sock"
    ```
    *   `DEVICES="/dev/serial0"` is the most important line. It tells `gpsd` to use the Pi's hardware serial port.
    *   `USBAUTO="false"` prevents `gpsd` from trying to find a USB GPS device.

4.  **Save and Exit:** Press `Ctrl+O` to save, then `Enter`, then `Ctrl+X` to exit the editor.
5.  **Restart and Enable `gpsd`:**
    ```bash
    sudo systemctl restart gpsd
    sudo systemctl enable gpsd
    ```
    `gpsd` will now start automatically every time you boot your Pi.

---

## Part 5: Reading Clean GPS Data (Terminal)

Now that `gpsd` is running, you can use a client program to see the parsed data.

1.  **Run `cgps`:**
    ```bash
    cgps -s
    ```
2.  **View the Output:** A new window will appear in your terminal. Once the GPS module gets a satellite fix, this screen will update in real-time with your:
    *   Latitude and Longitude
    *   Time & Date
    *   Altitude
    *   Speed and Heading
    *   A list of visible satellites

3.  **Exit `cgps`:** Press `Ctrl+C` to exit.

---

## Part 6: Accessing GPS Data with Python

You can easily get GPS data in your own projects using a Python library that connects to `gpsd`.

1.  **Install the Python Library:**
    ```bash
    sudo pip3 install gpsd-py3
    ```
2.  **Create a Python Script:** Create a file named `gps_test.py`:
    ```python
    # gps_test.py
    import gpsd
    import time

    def get_gps_data():
        """Connects to the local gpsd daemon and prints current GPS data."""
        try:
            # Connect to the local gpsd daemon
            print("Connecting to gpsd...")
            gpsd.connect()
            print("Connection successful.")

            while True:
                # Get the current GPS packet of data
                packet = gpsd.get_current()

                # Check if the packet has a 2D or 3D fix
                if packet.mode >= 2:
                    print("\n--- GPS FIX ---")
                    print(f"  Time (UTC): {packet.time}")
                    print(f"  Latitude:   {packet.lat:.6f}")
                    print(f"  Longitude:  {packet.lon:.6f}")
                    print(f"  Altitude:   {packet.alt:.2f} m")
                    print(f"  Speed:      {packet.speed:.2f} m/s")
                else:
                    print("Waiting for GPS fix...")

                time.sleep(2) # Wait 2 seconds before the next update

        except ConnectionRefusedError:
            print("Error: Could not connect to gpsd. Is it running?")
        except KeyboardInterrupt:
            print("\nExiting GPS client.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    if __name__ == "__main__":
        get_gps_data()
    ```
3.  **Run the Script:**
    ```bash
    python3 gps_test.py
    ```
    The script will connect to `gpsd` and start printing your location data once a fix is acquired.

---

## Part 7: Troubleshooting

*   **No data in `minicom`:** Check your hardware. Is the HAT seated correctly? Is the Pi powered on?
*   **`cgps` shows "NO FIX":** The GPS needs a clear view of the sky. Move the antenna near a window or outside. It can take a few minutes to get the first fix (a "cold start").
*   **Permission Denied error:** Your user might not have permission to access the serial port. Add your user to the `dialout` group: `sudo adduser $USER dialout`. You will need to log out and log back in for the change to take effect.
*   **`gpsd` connection refused in Python:** Make sure the `gpsd` service is running (`sudo systemctl status gpsd`). Check that your `/etc/default/gpsd` file is configured correctly and that you have restarted the service.
