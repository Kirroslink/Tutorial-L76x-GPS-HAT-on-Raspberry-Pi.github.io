
import os
import time
import serial
import pynmea2
import piexif
from picamera2 import Picamera2
from gpiod import Chip, Line, Edge
from threading import Thread
from datetime import datetime

# --- Configuration ---
# GPIO pin connected to the GPS module's PPS (Pulse Per Second) output
PPS_PIN = 17
# Serial port connected to the GPS module
SERIAL_PORT = "/dev/ttyS0"
# Baud rate for the GPS module
BAUD_RATE = 9600
# Directory to save photos
OUTPUT_DIR = "gps_photos"

# --- Global variables ---
# This will be accessed by both the GPS thread and the main thread
# It's volatile, but for this simple use case, a lock is not strictly necessary
latest_gps_data = {
    "fix": None,
    "timestamp": None,
    "latitude": None,
    "longitude": None,
}

def gps_parsing_thread():
    """
    A thread that continuously reads from the serial port, parses NMEA sentences,
    and updates the global `latest_gps_data` dictionary.
    """
    print("GPS thread started: Reading from serial port...")
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        while True:
            line = ser.readline().decode('utf-8', errors='ignore')
            if line.startswith('$GPRMC') or line.startswith('$GPGGA'):
                try:
                    msg = pynmea2.parse(line)
                    if msg.is_valid:
                        latest_gps_data["fix"] = True
                        if isinstance(msg, pynmea2.types.talker.RMC):
                           latest_gps_data["timestamp"] = msg.datetime
                        if hasattr(msg, 'latitude'):
                           latest_gps_data["latitude"] = msg.latitude
                        if hasattr(msg, 'longitude'):
                           latest_gps_data["longitude"] = msg.longitude
                except pynmea2.ParseError:
                    continue # Ignore sentences that can't be parsed
    except serial.SerialException as e:
        print(f"FATAL: Could not open serial port {SERIAL_PORT}: {e}")
        print("GPS thread exiting.")
        latest_gps_data["fix"] = False # Signal an error to the main thread

def format_gps_for_exif(degrees, direction):
    """
    Converts a decimal degree coordinate into the EXIF format (degrees, minutes, seconds).
    """
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = (degrees - d - m/60) * 3600
    # EXIF format is a tuple of tuples: (degrees, minutes, seconds)
    # Each value is a tuple of (numerator, denominator)
    return ((d, 1), (m, 1), (int(s * 100), 100))

def save_photo_with_exif(image_data, gps_info):
    """
    Saves the image data as a JPEG file with GPS EXIF tags.
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Convert GPS data
    lat_exif = format_gps_for_exif(gps_info["latitude"], "N" if gps_info["latitude"] > 0 else "S")
    lon_exif = format_gps_for_exif(gps_info["longitude"], "E" if gps_info["longitude"] > 0 else "W")

    # Create EXIF data dictionary
    exif_dict = {
        "GPS": {
            piexif.GPSIFD.GPSLatitudeRef: "N" if gps_info["latitude"] > 0 else "S",
            piexif.GPSIFD.GPSLatitude: lat_exif,
            piexif.GPSIFD.GPSLongitudeRef: "E" if gps_info["longitude"] > 0 else "W",
            piexif.GPSIFD.GPSLongitude: lon_exif,
            piexif.GPSIFD.GPSDateStamp: gps_info["timestamp"].strftime("%Y:%m:%d"),
            piexif.GPSIFD.GPSTimeStamp: [
                (gps_info["timestamp"].hour, 1),
                (gps_info["timestamp"].minute, 1),
                (gps_info["timestamp"].second, 1),
            ],
        }
    }
    exif_bytes = piexif.dump(exif_dict)

    # Generate filename and save
    filename = f"capture_{gps_info['timestamp'].strftime('%Y%m%d_%H%M%S')}.jpg"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(image_data)
    
    # Insert EXIF data into the saved file
    piexif.insert(exif_bytes, filepath)
    print(f"Saved photo with GPS data: {filepath}")

def pps_callback(event):
    """
    This function is called on the rising edge of the PPS signal.
    It triggers the camera capture.
    """
    print(f"PPS signal detected at {event.timestamp_ns}!")
    
    if not latest_gps_data.get("fix"):
        print("Skipping capture: No valid GPS fix yet.")
        return

    # Trigger a capture and get the raw data
    # The actual saving is done in the main loop to keep the callback fast
    request = picam2.capture_request()
    if request:
        image_data = request.make_buffer("main")
        metadata = request.get_metadata()
        
        # Pass the data to be saved
        save_photo_with_exif(image_data, latest_gps_data)
        
        request.release()


if __name__ == "__main__":
    # Start the GPS parsing thread
    gps_thread = Thread(target=gps_parsing_thread, daemon=True)
    gps_thread.start()

    # Initialize the camera
    picam2 = Picamera2()
    config = picam2.create_still_configuration(main={"size": (1920, 1080)})
    picam2.configure(config)
    picam2.start()
    print("Camera initialized.")
    time.sleep(2) # Give camera time to adjust

    # Set up GPIO for PPS signal using gpiod
    try:
        chip = Chip('gpiochip4') # On RPi 5 it's gpiochip4, on RPi 4 it's gpiochip0
        pps_line = chip.get_line(PPS_PIN)
        
        pps_line.request(
            "pps-cam-trigger",
            type=Line.Request.EVENT_RISING_EDGE
        )
        print(f"Monitoring GPIO pin {PPS_PIN} for PPS signal...")

        # Main loop - wait for PPS events
        while True:
            if not gps_thread.is_alive():
                print("GPS thread has stopped. Exiting main loop.")
                break
                
            if pps_line.has_event():
                event = pps_line.read_edge_event()
                pps_callback(event)

            time.sleep(0.01) # Small sleep to prevent busy-waiting

    except FileNotFoundError:
        print("ERROR: Could not find GPIO chip. On RPi 4, it's 'gpiochip0'. On RPi 5, it's 'gpiochip4'.")
        print("Please check the 'chip = Chip(...)' line in the script.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Cleaning up...")
        if 'picam2' in locals() and picam2.is_open:
            picam2.stop()
        if 'pps_line' in locals():
            pps_line.release()
        print("Exited.")
