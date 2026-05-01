# ======================================================
# RFID ACCESS CONTROL SYSTEM + OLED DISPLAY
# File Name: RFID_ACCESS_CONTROL_SYSTEM_OLED_DISPLAY.py
# ======================================================

from mfrc522 import MFRC522
from machine import Pin, PWM, I2C
import utime
import ssd1306

# =========================
# CONFIGURATION
# =========================
DEFAULT_KEY = [0xFF] * 6
BLOCK_ADDR = 1

AUTHORIZED_USERS = [
    {"uid": [39, 32, 240, 6], "name": "STU001"},
    {"uid": [23, 4, 132, 200], "name": "STU002"},
     {"uid": [1, 245, 22, 93], "name": "STU002"}
    
]

# =========================
# OLED SETUP (I2C)
# =========================
i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

def oled_show(line1="", line2="", line3="", line4=""):
    oled.fill(0)
    oled.text(line1, 0, 0)
    oled.text(line2, 0, 16)
    oled.text(line3, 0, 32)
    oled.text(line4, 0, 48)
    oled.show()

# =========================
# HARDWARE SETUP
# =========================
reader = MFRC522(sck=10, mosi=11, miso=12, rst=8, cs=13)

green_led = Pin(16, Pin.OUT)
red_led = Pin(17, Pin.OUT)
buzzer = Pin(18, Pin.OUT)

servo = PWM(Pin(15))
servo.freq(50)

# =========================
# SERVO
# =========================
def servo_angle(angle):
    duty = int(1638 + (angle / 180) * 8192)
    servo.duty_u16(duty)

def lock_door():
    servo_angle(0)

def unlock_door():
    servo_angle(90)

# =========================
# BUZZER
# =========================
def beep_success():
    for _ in range(2):
        buzzer.on()
        utime.sleep(0.1)
        buzzer.off()
        utime.sleep(0.1)

def beep_error():
    for _ in range(3):
        buzzer.on()
        utime.sleep(0.2)
        buzzer.off()
        utime.sleep(0.1)

# =========================
# LED
# =========================
def access_granted():
    green_led.on()
    red_led.off()

def access_denied():
    red_led.on()
    green_led.off()

def reset_led():
    green_led.off()
    red_led.off()

# =========================
# RFID
# =========================
def read_card():
    (stat, _) = reader.request(reader.REQIDL)
    if stat == reader.OK:

        (stat, uid) = reader.SelectTagSN()
        if stat == reader.OK:

            if reader.auth(reader.AUTHENT1A, BLOCK_ADDR, DEFAULT_KEY, uid) == reader.OK:
                (stat, data) = reader.read(BLOCK_ADDR)

                if stat == reader.OK:
                    text = ''.join(chr(i) for i in data if 32 <= i <= 126)
                    reader.stop_crypto1()
                    return uid, text

    return None, None

# =========================
# AUTH CHECK
# =========================
def is_authorized(uid, name):
    for user in AUTHORIZED_USERS:
        if user["uid"] == uid and user["name"] == name:
            return True
    return False

# =========================
# START SYSTEM
# =========================
print("=== SYSTEM READY ===")

oled_show("RFID SYSTEM", "Ready...", "", "")
lock_door()

last_uid = None

# =========================
# MAIN LOOP
# =========================
while True:
    reader.init()

    oled_show("Scan Card...", "", "", "")

    uid, name = read_card()

    if uid is not None:

        if uid == last_uid:
            utime.sleep_ms(500)
            continue

        last_uid = uid

        print("\nCard detected:", uid, name)

        oled_show("Card Detected", "UID OK", "", "")

        if is_authorized(uid, name):
            print("ACCESS GRANTED")

            access_granted()
            beep_success()

            oled_show("ACCESS GRANTED", name, "Door Unlock", "")

            unlock_door()
            utime.sleep(3)

            lock_door()
            reset_led()

        else:
            print("ACCESS DENIED")

            access_denied()
            beep_error()

            oled_show("ACCESS DENIED", "Unauthorized", "", "")

            utime.sleep(2)
            reset_led()

    utime.sleep_ms(300)