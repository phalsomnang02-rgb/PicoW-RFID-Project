from mfrc522 import MFRC522
import utime

# =========================
# CONFIGURATION
# =========================
DEFAULT_KEY = [0xFF] * 6
BLOCK_ADDR = 1   # Block 1 (Sector 0)

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

print("=== RFID READ BLOCK SYSTEM ===")
print("Place card near reader...\n")

last_uid = None  # Prevent repeated reading

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

            # Avoid repeated reading of same card
            if uid == last_uid:
                utime.sleep_ms(500)
                continue

            last_uid = uid

            print("\n🔹 Card detected!")
            print("UID:", uid)

            # Step 3: Authenticate
            if reader.auth(reader.AUTHENT1A, BLOCK_ADDR, DEFAULT_KEY, uid) == reader.OK:
                print("✅ Authentication SUCCESS")


                # Step 4: Read block
                (stat, data) = reader.read(BLOCK_ADDR)

                if stat == reader.OK:
                    print("📦 Raw Data:", data)
                                        # Convert to readable string
                    text = ''.join(chr(i) for i in data if 32 <= i <= 126)
                    print("📝 Text Data:", text if text else "[No readable text]")

                else:
                    print("❌ Read FAILED")

                reader.stop_crypto1()

            else:
                print("❌ Authentication FAILED")

    utime.sleep_ms(300)



