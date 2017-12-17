#!/usr/bin/env python

from flask import Flask
from flask import request
from flask import render_template
from flask import redirect, url_for
import time
import atexit
from neopixel import *
import signal
import sys

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# LED strip configuration:
LED_COUNT = 300      # Number of LED pixels.
LED_PIN = 18      # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
# True to invert the signal (when using NPN transistor level shift)
LED_INVERT = False
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

app = Flask(__name__)
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
animating = False

def signal_handler(signal, frame):
    colorWipe(strip, Color(0, 0, 0))
    sys.exit(0)


def print_date_time():
    print time.strftime("%A, %d. %B %Y %I:%M:%S %p")
    rainbow(strip)


def configure_schedule():
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
        func=print_date_time,
        trigger=IntervalTrigger(seconds=20),
        id='printing_job',
        name='Print date and time every five seconds',
        replace_existing=True)
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

def wheel(pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
                return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
                pos -= 85
                return Color(255 - pos * 3, 0, pos * 3)
        else:
                pos -= 170
                return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=40, iterations=1):
    global animating

    """Draw rainbow that fades across all pixels at once."""
    if animating == True:
        print 'Will not animate, already busy'
        return

    print 'Start animation'
    animating = True
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)
    animating = False
    print 'Done animating'

def light_up():
    print 'starting lights'
    strip.begin()

def set_color(color):
    print 'going color'
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show() 

@app.route('/white')
def white():
    set_color(Color(127,127,127))
    return 'made white'

@app.route('/red')
def red():
    set_color(Color(200,10,10))
    return 'set red'

@app.route('/quit')
def quit():
    return "Quitting..."

if __name__ == '__main__':
    app.debug = True
    light_up()
    white()
    # configure_schedule()
    app.run(host='0.0.0.0')
