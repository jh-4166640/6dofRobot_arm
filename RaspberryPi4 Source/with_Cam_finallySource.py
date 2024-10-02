import torch
import cv2
from picamera2 import Picamera2
from flask import Flask, Response
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
import threading
import serial  # for serial communication

# Pin Definitions for Wheel 1
CW_PIN_1 = 17
GNDC_PIN_1 = 27
ON_PIN_1 = 22
GND_PIN_1 = 23

# Pin Definitions for Wheel 2
CW_PIN_2 = 18
GNDC_PIN_2 = 24
ON_PIN_2 = 25
GND_PIN_2 = 5

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(CW_PIN_1, GPIO.OUT)
GPIO.setup(GNDC_PIN_1, GPIO.OUT)
GPIO.setup(ON_PIN_1, GPIO.OUT)
GPIO.setup(GND_PIN_1, GPIO.OUT)

GPIO.setup(CW_PIN_2, GPIO.OUT)
GPIO.setup(GNDC_PIN_2, GPIO.OUT)
GPIO.setup(ON_PIN_2, GPIO.OUT)
GPIO.setup(GND_PIN_2, GPIO.OUT)

# Initialize GPIO
GPIO.output(CW_PIN_1, GPIO.LOW)
GPIO.output(GNDC_PIN_1, GPIO.LOW)
GPIO.output(ON_PIN_1, GPIO.HIGH)
GPIO.output(GND_PIN_1, GPIO.HIGH)

GPIO.output(CW_PIN_2, GPIO.LOW)
GPIO.output(GNDC_PIN_2, GPIO.LOW)
GPIO.output(ON_PIN_2, GPIO.HIGH)
GPIO.output(GND_PIN_2, GPIO.HIGH)

# Flask App for Video Streaming
app = Flask(__name__)

def setupCam():
    cam = Picamera2()
    cam.start(show_preview=False)
    return cam

def generate_frames(cam):
    while True:
        frame = cam.capture_array()

        # RGB to BGR conversion (OpenCV uses BGR format)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Flip the frame horizontally and vertically
        frame = cv2.flip(frame, 1)  # Horizontal flip
        frame = cv2.flip(frame, 0)  # Vertical flip

        # Convert frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(cam), mimetype='multipart/x-mixed-replace; boundary=frame')

# Wheel Control Functions
def move_forward():
    print("Both Wheels Moving Forward")
    GPIO.output(ON_PIN_1, GPIO.LOW)
    GPIO.output(GND_PIN_1, GPIO.LOW)
    GPIO.output(CW_PIN_1, GPIO.LOW)
    GPIO.output(GNDC_PIN_1, GPIO.LOW)

    GPIO.output(ON_PIN_2, GPIO.LOW)
    GPIO.output(GND_PIN_2, GPIO.LOW)
    GPIO.output(CW_PIN_2, GPIO.LOW)
    GPIO.output(GNDC_PIN_2, GPIO.LOW)

def move_backward():
    print("Both Wheels Moving Backward")
    GPIO.output(ON_PIN_1, GPIO.LOW)
    GPIO.output(GND_PIN_1, GPIO.LOW)
    GPIO.output(CW_PIN_1, GPIO.HIGH)
    GPIO.output(GNDC_PIN_1, GPIO.HIGH)

    GPIO.output(ON_PIN_2, GPIO.LOW)
    GPIO.output(GND_PIN_2, GPIO.LOW)
    GPIO.output(CW_PIN_2, GPIO.HIGH)
    GPIO.output(GNDC_PIN_2, GPIO.HIGH)

def turn_left():
    print("Turning Left")
    GPIO.output(ON_PIN_1, GPIO.LOW)
    GPIO.output(GND_PIN_1, GPIO.LOW)
    GPIO.output(CW_PIN_1, GPIO.HIGH)
    GPIO.output(GNDC_PIN_1, GPIO.HIGH)

    GPIO.output(ON_PIN_2, GPIO.LOW)
    GPIO.output(GND_PIN_2, GPIO.LOW)
    GPIO.output(CW_PIN_2, GPIO.LOW)
    GPIO.output(GNDC_PIN_2, GPIO.LOW)

def turn_right():
    print("Turning Right")
    GPIO.output(ON_PIN_1, GPIO.LOW)
    GPIO.output(GND_PIN_1, GPIO.LOW)
    GPIO.output(CW_PIN_1, GPIO.LOW)
    GPIO.output(GNDC_PIN_1, GPIO.LOW)

    GPIO.output(ON_PIN_2, GPIO.LOW)
    GPIO.output(GND_PIN_2, GPIO.LOW)
    GPIO.output(CW_PIN_2, GPIO.HIGH)
    GPIO.output(GNDC_PIN_2, GPIO.HIGH)

def stop_all_movement():
    print("Stopping Both Wheels")
    GPIO.output(ON_PIN_1, GPIO.HIGH)
    GPIO.output(GND_PIN_1, GPIO.HIGH)
    GPIO.output(CW_PIN_1, GPIO.LOW)
    GPIO.output(GNDC_PIN_1, GPIO.LOW)

    GPIO.output(ON_PIN_2, GPIO.HIGH)
    GPIO.output(GND_PIN_2, GPIO.HIGH)
    GPIO.output(CW_PIN_2, GPIO.LOW)
    GPIO.output(GNDC_PIN_2, GPIO.LOW)

# MQTT Callbacks and Wheel Control
def on_connect(client, userdata, flags, rc):
    global flag_connected
    flag_connected = 1
    client_subscriptions(client)
    print("Connected to MQTT server")

def on_disconnect(client, userdata, rc):
    global flag_connected
    flag_connected = 0
    print("Disconnected from MQTT server")

def callback_esp32_sensor1(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    print('ESP sensor1 data:', payload)

    if payload == '1':
        move_forward()
    elif payload == '2':
        move_backward()
    elif payload == '3':
        turn_left()
    elif payload == '4':
        turn_right()
    elif payload == '0':
        stop_all_movement()
    else:
        # Send command to Robot Arm via serial
        command = payload.strip()
        try:
            ser.write(command.encode('utf-8'))
            print(f"Send to Robot Arm: {command}")
        except Exception as e:
            print(f"Failed to send command to Robot Arm: {e}")

# MQTT Client Subscriptions
def client_subscriptions(client):
    client.subscribe("esp32/sensor1")

# Thread for running Flask server
def flask_thread():
    global cam
    cam = setupCam()
    app.run(host='0.0.0.0', port=5000)

# Main function for running both Flask and MQTT
def main():
    # MQTT Client Setup
    client = mqtt.Client("rpi_client1")
    global flag_connected
    flag_connected = 0

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.message_callback_add('esp32/sensor1', callback_esp32_sensor1)

    client.connect('192.168.137.69', 1883)
    client.loop_start()
    client_subscriptions(client)

    # Serial Communication with Robot Arm via GPIO (TX/RX)
    try:
        global ser
        ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)  # Use /dev/serial0 for GPIO UART
        if ser.is_open:
            print("Serial communication with Robot Arm initialized via GPIO (TX/RX)")

        # Start Flask server in a new thread
        threading.Thread(target=flask_thread, daemon=True).start()

        # Main loop for checking MQTT connection and serial communication
        while True:
            time.sleep(4)
            if flag_connected != 1:
                print("Trying to connect to MQTT server...")

            # Read from serial if data is available
            if ser.in_waiting > 0:
                arduino_response = ser.readline().decode('utf-8').strip()
                print("Received from Arduino:", arduino_response)

    except serial.SerialException as e:
        print(f"Error with Serial communication: {e}")
    except KeyboardInterrupt:
        print("Terminating...")

    finally:
        ser.close()
        GPIO.cleanup()
        client.loop_stop()
        print("GPIO resources cleaned up")

if __name__ == '__main__':
    main()
