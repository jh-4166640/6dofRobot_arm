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

#GPIO.setup(RX, GPIO.OUT)
#GPIO.setup(TX, GPIO.OUT)

# Initialize GPIO
GPIO.output(CW_PIN_1, GPIO.LOW)
GPIO.output(GNDC_PIN_1, GPIO.LOW)
GPIO.output(ON_PIN_1, GPIO.HIGH)
GPIO.output(GND_PIN_1, GPIO.HIGH)

GPIO.output(CW_PIN_2, GPIO.LOW)
GPIO.output(GNDC_PIN_2, GPIO.LOW)
GPIO.output(ON_PIN_2, GPIO.HIGH)
GPIO.output(GND_PIN_2, GPIO.HIGH)

#GPIO.output(RX, GPIO.OUT)
#GPIO.output(TX, GPIO.OUT)

# MQTT Callbacks and Wheel Control Functions
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
        #print("Turning left")
        move_forward()
    elif payload == '2':
        #print("Turning right")
        move_backward()
    elif payload == '3':
        #print("Moving backward")
        turn_right()
    elif payload == '4':
        #print("Moving forward")
        turn_left()
    elif payload == '0':
        #print("Stopping All Movements")
        stop_all_movement()
    else:
        # 로봇 팔 명령 처리
        command = payload.strip()  # 명령을 적절하게 포맷팅
        try:
            ser.write(command.encode('utf-8'))
            print(f"Send to RobotArm: {command}")
        except Exception as e:
            print(f"Failed to send command to Robot Arm: {e}")

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
    #print("Both Wheels Moving Backward")
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

# MQTT Client Subscriptions
def client_subscriptions(client):
    client.subscribe("esp32/sensor1")

# MQTT Client Setup
client = mqtt.Client("rpi_client1")
flag_connected = 0

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.message_callback_add('esp32/sensor1', callback_esp32_sensor1)

client.connect('0.0.0.0', 1883)
client.loop_start()
client_subscriptions(client)

print("...client setup complete...")

# Serial Communication with Robot Arm via GPIO (TX/RX)
try:
    ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)  # Use /dev/serial0 for GPIO UART
    if ser.is_open:
        print("Serial communication with Robot Arm initialized via GPIO (TX/RX)")
        
    while True:
        time.sleep(4)
        if flag_connected != 1:
            print("Trying to connect to MQTT server...")

        # Read from serial if data is available
        if ser.in_waiting > 0:
            arduino_response = ser.readline().decode('utf-8').strip()  # Read the Arduino response
            print("Received from Arduino:", arduino_response)
        
except serial.SerialException as e:
    print(f"Error with Serial communication: {e}")
except KeyboardInterrupt:
    print("Terminating...")

finally:
    ser.close()  # Ensure the serial port is closed
    GPIO.cleanup()
    client.loop_stop()
    print("GPIO resources cleaned up")
