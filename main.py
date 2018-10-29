import machine
import time

import bme280
import ds18x20, onewire
import ssd1306


# Global values:
MOTION = False     # motrion detection
DISPLAY = 0        # display on|off
BME_T = 0          # 
BME_P = 0          # BME280 data
BME_H = 0          #
DS_T = 0           # DS18X20 temperature

# Global timers
tmr_bme = 60        # data reading frequency in sec
tmr_bme_last = 0
tmr_ds = 60
tmr_ds_last = 0
tmr_mqtt = 60      # data sendint frequency
tmr_mqtt_last = 0
tmr_display_off = 20
tmr_display_off_last = 0

# I2C Init
pinScl      = 5   # ESP8266 GPIO5 (D1)
pinSda      = 4   # ESP8266 GPIO4 (D2)
print('i2c init')
i2c = machine.I2C(scl=machine.Pin(pinScl), sda=machine.Pin(pinSda)) 


#############################################
#  PIR                                      #
#############################################
pir_pin = machine.Pin(14, machine.Pin.IN)
pir_old_value = pir_pin.value()

def check_motion():
    global MOTION
    global pir_old_value
    if pir_pin.value():
        if not pir_old_value:
            print('Motion detected')
            MOTION = True
    else:
        if pir_old_value:
            print('No motion')
            MOTION = False
    pir_old_value = pir_pin.value()


#############################################
#  BME280                                   #
#############################################
addrBME280  = 118 # 0x76

def read_bme(bme): 
    global BME_T
    global BME_P
    global BME_H
    global tmr_bme_last
    if time.time() - tmr_bme_last > tmr_bme:
        print('BME280 reading data')
        bme_data = bme.read_compensated_data()
        BME_T = bme_data[0]/100              # degrees Celsius
        BME_P = bme_data[1]/256/100000*750   # mm Hg 
        BME_H = bme_data[2]/1024             # relative humidity
        tmr_bme_last = time.time()
        print(BME_T, BME_P, BME_H)
    else:
        print('BME280 timer pass')
        pass


#############################################
#  DS18X20                                  #
#############################################
print('One Wire init')
oneWire_pin = machine.Pin(2)

def read_ds(rom):
    global DS_T
    global tmr_ds_last
    if time.time() - tmr_ds_last > tmr_ds:
        print('DS18X20 reading data')
        DS_T = ds.read_temp(rom)
        print(DS_T)
        tmr_ds_last = time.time()
    else:
        print('DS1820 timer pass')
        pass


#############################################
#  OLED                                     #
#############################################

def oled_on (display):
    display.fill(0)
    display.text('T in:%s' % '{:.0f}'.format(BME_T), 0, 4, 1)
    display.text('out:%s' % '{:.0f}'.format(DS_T), 70, 4, 1)
    display.text('P:%smm' % '{:.0f}'.format(BME_P), 0, 24, 1)
    display.text('H:%s' % '{:.0f}'.format(BME_H) + '%', 72, 24, 1)
    print('Display ON')
    display.show()

def oled_off(display):
    global tmr_display_off_last
    if time.time() - tmr_display_off_last > tmr_display_off:
        display.fill(0)
        print('Display OFF')
        display.show()
        tmr_display_off_last = time.time()
    else:
        print('Display timer pass')



#############################################
#  MQTT                                     #
#############################################



print('BME280 init')
bme = bme280.BME280(i2c=i2c,address=addrBME280)

print('DS18X20 init')
ds = ds18x20.DS18X20(onewire.OneWire(oneWire_pin))
roms =  ds.scan()
ds.convert_temp()
time.sleep_ms(750)

print('OLED init')
display = ssd1306.SSD1306_I2C(128, 32, i2c)
display.contrast(0)

tmr_bme_last = time.time() - tmr_bme
tmr_ds_last = time.time() - tmr_ds
tmr_display_off_last = time.time() - tmr_display_off
tmr_mqtt_last = time.time() - tmr_mqtt

while True:
    check_motion()
    read_bme(bme)
    read_ds(roms[0])
    if MOTION: 
        oled_on(display)
    else:
        oled_off(display)
    time.sleep(1)