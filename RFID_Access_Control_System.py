# ============================================
# RFID ACCESS CONTROL SYSTEM (FINAL VERSION)
# UID + NAME MATCH (HIGH SECURITY)
# ============================================

from mfrc522 import MFRC522
from machine import Pin, PWM
import utime

# =========================
# CONFIGURATION
# =========================
DEFAULT_KEY = [0xFF] * 6
BLOCK_ADDR = 1  # Block storing NAME

# Authorized Database (UID + NAME must match)
AUTHORIZED_USERS = [
    {
         "uid": [1, 245, 22, 93],"name": "Phal Somnang"},
]

# =========================
# HARDWARE SETUP
# =========================
reader = MFRC522(
    sck=10,
    mosi=11,
    miso=12,
    rst=8,
    cs=13,
    spi_id=1
)

green_led = Pin(16, Pin.OUT)
red_led = Pin(17, Pin.OUT)
buzzer = Pin(18, Pin.OUT)

servo = PWM(Pin(15))
servo.freq(50)

# =========================
# SERVO CONTROL
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
# LED CONTROL
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
# RFID FUNCTIONS
# =========================
def read_card():
    (stat, _) = reader.request(reader.REQIDL)
    if stat == reader.OK:

        (stat, uid) = reader.SelectTagSN()
        if stat == reader.OK:

            # Authenticate block
            if reader.auth(reader.AUTHENT1A, BLOCK_ADDR, DEFAULT_KEY, uid) == reader.OK:
                (stat, data) = reader.read(BLOCK_ADDR)

                if stat == reader.OK:
                    text = ''.join(chr(i) for i in data if 32 <= i <= 126)
                    reader.stop_crypto1()
                    return uid, text

    return None, None

# =========================
# AUTHENTICATION LOGIC
# =========================
def is_authorized(uid, name):
    for user in AUTHORIZED_USERS:
        if user["uid"] == uid and user["name"] == name:
            return True
    return False

# =========================
# MAIN SYSTEM
# =========================
print("=== RFID ACCESS CONTROL SYSTEM READY ===")
lock_door()

last_uid = None

while True:
    reader.init()

    uid, name = read_card()

    if uid is not None:

        # Prevent duplicate scans
        if uid == last_uid:
            utime.sleep_ms(500)
            continue

        last_uid = uid

        print("\n🔹 Card detected")
        print("UID:", uid)
        print("Name:", name)

        if is_authorized(uid, name):
            print("ACCESS GRANTED")

            access_granted()
            beep_success()

            unlock_door()
            utime.sleep(3)

            lock_door()
            reset_led()

        else:
            print("ACCESS DENIED")

            access_denied()
            beep_error()

            utime.sleep(2)
            reset_led()

    utime.sleep_ms(300)