import machine
import time

# i2c pins
pinScl      = 5   # ESP8266 GPIO5 (D1)
pinSda      = 4   # ESP8266 GPIO4 (D2)

# init i2c object
print('i2c init...')
i2c = machine.I2C(scl=machine.Pin(pinScl), sda=machine.Pin(pinSda)) 
print('OK')

time.sleep_ms(2000)

####################################################################
#test bme280
print('*** Testing bme280... ***')
import bme280

addrBME280  = 118 # 0x76
print('bme280 init...')
bme = bme280.BME280(i2c=i2c,address=addrBME280)
print('OK')

print('reading bme280 data...')
bme_data = bme.read_compensated_data()
temp = bme_data[0]/100              # degrees Celsius
pres = bme_data[1]/256/100000*750   # mm Hg 
humi = bme_data[2]/1024             # relative humidity

print(bme_data[0])
print(bme_data[1])
print(bme_data[2])

print('t=',temp)
print('p=',pres)
print('h=',humi)

time.sleep_ms(2000)

#####################################################################
#test DS18B20
print('*** Testing DS18B20... ***')
import onewire, ds18x20

# 1w data pin
data = machine.Pin(2)

# init 1w object
print('1-wire init...')
ds = ds18x20.DS18X20(onewire.OneWire(data))
print('OK')

roms =  ds.scan()
ds.convert_temp()
time.sleep_ms(750)
temp_1w = ds.read_temp(roms[0])
print('t=', temp_1w)

time.sleep_ms(2000)


####################################################################
# test OLED
print('*** Testing display... ***')

import ssd1306

# init display
print('display init...')
display = ssd1306.SSD1306_I2C(128, 32, i2c)  #почем адрес захардкожен?
print('OK')

display.fill(0)
display.text('Hello! =)', 10, 10, 1)
display.show()
time.sleep_ms(5000)
display.fill(0)
display.show()

####################################################################
# test PIR

#cpprint('*** Testing display... ***')

