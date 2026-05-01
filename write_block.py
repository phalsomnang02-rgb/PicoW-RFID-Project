from mfrc522 import MFRC522
import utime

# =========================
# CONFIGURATION
# =========================
DEFAULT_KEY = [0xFF] * 6
BLOCK_ADDR = 1   # Block 1 (Sector 0)

# Data to write (max 16 characters)
DATA_TO_WRITE = "Unknow name"

# =========================
# INITIALIZE RFID
# =========================
reader = MFRC522(
    sck=10,
    mosi=11,
    miso=12,
    rst=8,
    cs=13,
    spi_id=1
)


print("=== RFID WRITE BLOCK SYSTEM ===")
print("Place card near reader to write...\n")

last_uid = None  # Prevent repeated writing

# =========================
# HELPER FUNCTION
# =========================
def prepare_data(text):
    """Convert string to 16-byte array"""
    data = [ord(c) for c in text]
    if len(data) > 16:
        data = data[:16]
    else:
        data += [0] * (16 - len(data))
    return data

# =========================
# MAIN LOOP
# =========================
while True:
    reader.init()

    # Step 1: Detect card
    (stat, tag_type) = reader.request(reader.REQIDL)

    if stat == reader.OK:

        # Step 2: Get UID
        (stat, uid) = reader.SelectTagSN()

        if stat == reader.OK:

            # Prevent rewriting same card repeatedly
            if uid == last_uid:
                utime.sleep_ms(500)
                continue

            last_uid = uid

            print("\n🔹 Card detected!")
            print("UID:", uid)

            # Step 3: Authenticate
            if reader.auth(reader.AUTHENT1A, BLOCK_ADDR, DEFAULT_KEY, uid) == reader.OK:
                print("✅ Authentication SUCCESS")

                # Prepare data
                data = prepare_data(DATA_TO_WRITE)

                print("📝 Writing Data:", DATA_TO_WRITE)

                # Step 4: Write block
                if reader.write(BLOCK_ADDR, data) == reader.OK:
                    print("✅ Write SUCCESS")

                    # Optional: Verify by reading back
                    (stat, verify_data) = reader.read(BLOCK_ADDR)

                    if stat == reader.OK:
                        text = ''.join(chr(i) for i in verify_data if 32 <= i <= 126)
                        print("🔍 Verified Data:", text)

                else:
                    print("❌ Write FAILED")

                reader.stop_crypto1()

            else:
                print("❌ Authentication FAILED")

    utime.sleep_ms(300)

