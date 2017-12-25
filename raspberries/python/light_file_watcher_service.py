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

GAMMA_VALUES = [
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
    1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
    2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
    5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
   10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
   17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
   25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
   37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
   51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
   69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
   90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
  115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
  144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
  177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
  215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255
]

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
red = 1
green = 1
blue = 1
speed = 1

class Lights:
  def __init__(self):
    self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    self.strip.begin()

  def animate(self):
      logging.debug('animate ...')
      if effect == 'rainbow':
        logging.debug('Should be rainbow')
        lights.rainbow()
      elif effect == 'chase':
        logging.debug('Should be chase')
        lights.theaterChaseRainbow()
      elif effect == 'rainbow_cycle':
        lights.rainbowCycle()
      elif effect == 'solid':
        red_total = max([0, int(255 * red * brightness)])
        green_total = max([0, int(255 * green * brightness)])
        blue_total = max([0, int(255 * blue * brightness)])
        logging.debug('Should be solid: ' + str(brightness) + ': [' + str(red_total) + ',' + str(green_total) + ',' + str(blue_total) + ']')
        lights.set_color(Color(red_total,green_total,blue_total))

  def rainbow(self, wait_ms=1, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
      for i in range(self.strip.numPixels()):
        if not be_on or effect != 'rainbow':
          return
        self.strip.setPixelColor(i, self.wheel((i+j) & 255))
      self.strip.show()
      time.sleep(self.sleep_time(wait_ms))

  def rainbowCycle(self, wait_ms=1, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
      for i in range(self.strip.numPixels()):
        if not be_on or effect != 'rainbow_cycle':
          return
        self.strip.setPixelColor(i, self.wheel((int(i * 256 / self.strip.numPixels()) + j) & 255))
      self.strip.show()
      time.sleep(self.sleep_time(wait_ms))

  def theaterChaseRainbow(self, wait_ms=1):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
      if not be_on or effect != 'chase':
        return
      logging.debug('Showing rainbow with brightness ' + str(brightness) + ', sleep_time: ' + str(self.sleep_time(wait_ms)))
      for q in range(3):
        for i in range(0, self.strip.numPixels(), 3):
          self.strip.setPixelColor(i+q, self.wheel((i+j) % 255))
        self.strip.show()
        time.sleep(self.sleep_time())
        for i in range(0, self.strip.numPixels(), 3):
          self.strip.setPixelColor(i+q, 0)

  def sleep_time(self, wait_ms = 1):
    result = (1000 * (1-speed)) * wait_ms / 1000.0
    if result < 0:
        return 0
    return result
    
  def off(self):
    self.set_color(Color(0,0,0))

  def set_color(self, color):
    logging.debug('going color')
    for i in range(self.strip.numPixels()):
        self.strip.setPixelColor(i, color)
    self.strip.show()

  def with_brightness(self, input):
      if brightness <= 0:
          return 0

      result = int(input * brightness)
      if result < 0:
          return 0
      gamma_corrected = GAMMA_VALUES[result]
      return gamma_corrected

  def wheel(self, pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
      return Color(self.with_brightness(red * pos * 3), self.with_brightness(green * 255 - pos * 3), 0)
    elif pos < 170:
      pos -= 85
      return Color(self.with_brightness(red * 255 - pos * 3), 0, self.with_brightness(blue * pos * 3))
    else:
      pos -= 170
      return Color(0, self.with_brightness(green * pos * 3), self.with_brightness(blue * 255 - pos * 3))

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
        global red
        global green
        global blue
        global speed

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
              if brightness < 1:
                brightness = brightness + .1
            elif event_name == 'dimmer':
              logging.debug('Should be dimmer: ' + str(brightness))
              if brightness > 0:
                brightness = brightness - .1
            elif event_name == 'red_more':
              if red < 1:
                red = red + .1
            elif event_name == 'red_less':
              if red > 0:
                red = red - .1
            elif event_name == 'blue_more':
              if blue < 1:
                blue = blue + .1
            elif event_name == 'blue_less':
              if blue > 0:
                blue = blue - .1
            elif event_name == 'green_more':
              if green < 1:
                green = green + .1
            elif event_name == 'green_less':
              if green > 0:
                green = green - .1
            elif event_name == 'faster':
              speed = speed + .1
            elif event_name == 'slower':
              speed = speed - .1


def subscriber(sender):
    print("Got a signal sent by %r" % sender)

lights = Lights()
example = LightRunner()

#example.run()

w = Watcher()
w.run()

