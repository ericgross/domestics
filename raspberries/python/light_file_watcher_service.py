import threading
import time

from neopixel import *

import argparse
import signal
import sys

import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename="/tmp/pi_listener.log", level=logging.DEBUG)


# LED strip configuration:
LED_COUNT      = 900      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

be_on = True

class Lights:
  def __init__(self):
    self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    self.strip.begin()

  def theaterChaseRainbow(self, wait_ms=1):
    """Rainbow movie theater light style chaser animation."""
    for j in range(6):
      for q in range(3):
        for i in range(0, self.strip.numPixels(), 3):
          self.strip.setPixelColor(i+q, self.wheel((i+j) % 255))
        self.strip.show()
        time.sleep(wait_ms/1000.0)
        for i in range(0, self.strip.numPixels(), 3):
          self.strip.setPixelColor(i+q, 0)

  def wheel(self, pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
      return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
      pos -= 85
      return Color(255 - pos * 3, 0, pos * 3)
    else:
      pos -= 170
      return Color(0, pos * 3, 255 - pos * 3)

class LightRunner(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, interval=1):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        """ Method that runs forever """
        while True:
            # Do something
            print('Doing something imporant in the background')

      if be_on:
              #time.sleep(self.interval)
              #lights = Lights()
              print 'Should be on ..'
              lights.theaterChaseRainbow()
            else:
              print 'Should be off..'

class Watcher:
    DIRECTORY_TO_WATCH = "/tmp/lights"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                print 'time!'
                time.sleep(5)
        except:
            self.observer.stop()
            print "Error"

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        global be_on

        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            print "Received created event - %s." % event.src_path

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print "Received modified event - %s." % event.src_path
            if event.src_path == '/tmp/lights/on':
              print 'Should turn on'
              be_on = True
            if event.src_path == '/tmp/lights/off':
              print 'Should turn off'
              be_on = False

lights = Lights()
example = LightRunner()

w = Watcher()
w.run()