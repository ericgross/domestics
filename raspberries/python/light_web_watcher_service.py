#!/usr/bin/env python

from flask import Flask
from flask import request
from flask import render_template
from flask import redirect, url_for
import sys
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename="/tmp/pi_listener.log", level=logging.DEBUG)

app = Flask(__name__)

def write_file(value):
 print 'Writing value to file: ' + value
 file = open('/tmp/lights/' + value,'w')
 file.write(value)
 file.close()
 return True

@app.route('/on')
def on():
    if write_file('on'):
      return 'turned on'

@app.route('/off')
def off():
    if write_file('off'):
      return 'turned off'

@app.route('/solid')
def solid():
    if write_file('solid'):
        return 'solid'

@app.route('/rainbow')
def rainbow():
    if write_file('rainbow'):
        return 'rainbow'

@app.route('/brighter')
def brighter():
    if write_file('brighter'):
        return 'brighter'

@app.route('/dimmer')
def dimmer():
    if write_file('dimmer'):
        return 'dimmer'

@app.route('/custom')
def custom():
    command = request.args.get('command')
    if write_file(command):
        return 'wrote custom command: ' + command

if __name__ == '__main__':
    app.debug = True

    if not os.path.exists('/tmp/lights'):
      os.makedirs('/tmp/lights')

    app.run(host='0.0.0.0')

