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
effect = 'rainbow'
brightness = 1

class Lights:
  def __init__(self):
    self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    self.strip.begin()

  def animate(self):
      if effect == 'rainbow':
        logging.debug('Should be rainbow')
        lights.rainbow()
      elif effect == 'chase':
        logging.debug('Should be chase')
        lights.theaterChaseRainbow()
      elif effect == 'rainbow_cycle':
        lights.rainbowCycle()
      elif effect == 'solid':
        logging.debug('Should be solid')
        lights.set_color(Color(int(30 * brightness),int(80 * brightness),int(100 * brightness)))

  def rainbow(self, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
      for i in range(self.strip.numPixels()):
        if effect != 'rainbow':
          return
        self.strip.setPixelColor(i, self.wheel((i+j) & 255))
      self.strip.show()
      time.sleep(wait_ms/1000.0)

  def rainbowCycle(self, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
      for i in range(self.strip.numPixels()):
        if effect != 'rainbow_cycle':
          return
        self.strip.setPixelColor(i, self.wheel((int(i * 256 / self.strip.numPixels()) + j) & 255))
      self.strip.show()
      time.sleep(wait_ms/1000.0)

  def theaterChaseRainbow(self, wait_ms=1):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
      if not be_on or effect != 'chase':
        return
      logging.debug('Showing rainbow with brightness ' + str(brightness))
      for q in range(3):
        for i in range(0, self.strip.numPixels(), 3):
          self.strip.setPixelColor(i+q, self.wheel((i+j) % 255))
        self.strip.show()
        time.sleep(wait_ms/1000.0)
        for i in range(0, self.strip.numPixels(), 3):
          self.strip.setPixelColor(i+q, 0)

  def off(self):
    self.set_color(Color(0,0,0))

  def set_color(self, color):
    logging.debug('going color')
    for i in range(self.strip.numPixels()):
        self.strip.setPixelColor(i, color)
    self.strip.show()

  def with_brightness(self, input):
      result = int(input * brightness)
      if result < 0:
          return 0
      return result

  def wheel(self, pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
      return Color(self.with_brightness(pos * 3), self.with_brightness(255 - pos * 3), 0)
    elif pos < 170:
      pos -= 85
      return Color(self.with_brightness(255 - pos * 3), 0, self.with_brightness(pos * 3))
    else:
      pos -= 170
      return Color(0, self.with_brightness(pos * 3), self.with_brightness(255 - pos * 3))

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

    def show_on(self):
      logging.debug('Should be on with brightness ' + str(brightness))
      lights.animate()

    def run(self):
        """ Method that runs forever """
        while True:
            # Do something
            time.sleep(1)
            logging.debug('Doing something imporant in the background')

            if be_on:
              self.show_on()
            else:
              logging.debug('Should be off..')
              lights.off()

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
                logging.debug('time!')
                time.sleep(1)
        except:
            self.observer.stop()
            logging.debug("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        global be_on
        global effect
        global brightness

        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            logging.debug("Received created event - %s." % event.src_path)

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            logging.debug("Received modified event - %s." % event.src_path)

            event_name = event.src_path.split('/')[-1]
            if event_name == 'on':
              logging.debug('Should turn on')
              be_on = True
              brightness = 1
            elif event_name == 'off':
              logging.debug('Should turn off')
              be_on = False
            elif event_name == 'rainbow':
              logging.debug('Should be rainbow')
              effect = 'rainbow'
            elif event_name == 'rainbow_cycle':
              effect = 'rainbow_cycle'
            elif event_name == 'solid':
              logging.debug('Should be solid')
              effect = 'solid'
            elif event_name == 'chase':
              logging.debug('Should be chase')
              effect = 'chase'
            elif event_name == 'brighter':
              logging.debug('Should be brighter')
              brightness = brightness + .1
            elif event_name == 'dimmer':
              logging.debug('Should be dimmer: ' + str(brightness))
              brightness = brightness - .1


def subscriber(sender):
    print("Got a signal sent by %r" % sender)

lights = Lights()
example = LightRunner()

#example.run()

w = Watcher()
w.run()

