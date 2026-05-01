from machine import Pin, I2C
import ssd1306

i2c = I2C(1, scl=Pin(7), sda=Pin(6))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

oled.fill(0)
oled.text("Hello, Pico!", 0, 0)
oled.text("RFID System", 0, 20)
oled.show()
