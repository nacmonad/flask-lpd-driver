from raspledstrip.ledstrip import LEDStrip
from raspledstrip.LPD8806 import LPD8806SPI
from raspledstrip.animation import AlertStrobe, FillFromCenter, BreathingLight, Nothing, Rainbow, RainbowCycle, ColorPattern, ColorWipe, ColorFade, ColorChase, PartyMode, FireFlies, LarsonScanner, LarsonRainbow, Wave, RGBClock
from raspledstrip.color import Color, wheel_color
import os
import gc
import json
#import threading
import time
from multiprocessing import Process

LED_LENGTH = 160
led_strip = LEDStrip(LPD8806SPI(LED_LENGTH))
led_strip.all_off()

from flask import Flask, request, jsonify
app = Flask(__name__)


animations = { 'None': Nothing, 'AlertStrobe': AlertStrobe, 'BreathingLight':BreathingLight, 'ColorFade':ColorFade, 'ColorPattern':ColorPattern, 'ColorChase':ColorChase, 'ColorWipe':ColorWipe, 'FillFromCenter':FillFromCenter, 'Rainbow': Rainbow, 'RainbowCycle': RainbowCycle, 'PartyMode':PartyMode, 'FireFlies':FireFlies, 'LarsonScanner':LarsonScanner, 'LarsonRainbow':LarsonRainbow, 'Wave': Wave, 'RGBClock': RGBClock }

current_color = {'red':128, 'green':128, 'blue':128}
current_proc = None
procs = []

def runSequenceInThread(sequence='None'):
    print "running a seuqnece in proc:"
    print sequence
    proc = os.getpid()
    print proc

    led_strip.all_off()
    if(sequence in ['Nothing','Rainbow', 'RainbowCycle']):
        animations[sequence](led_strip, 0, LED_LENGTH).run(1,30,50000)
    elif(sequence in ['BreathingLight']):
        animations[sequence](led_strip, current_color['red'], current_color['blue'], current_color['green'], 0.1,1.0,0,0).run(1,30,50000)
    elif(sequence in ['AlertStrobe', 'FillFromCenter', 'LarsonScanner']):
        animations[sequence](led_strip, Color(current_color['red'], current_color['blue'], current_color['green'], 1.0)).run(1,30,50000)
    elif(sequence in ['ColorPattern']):
	animations[sequence](led_strip, [Color(current_color['red'], current_color['blue'], current_color['green'], 1.0), wheel_color(10), wheel_color(42)], 8, True, 0, LED_LENGTH).run(1,30,50000)
    elif(sequence in ['ColorWipe']):
	animations[sequence](led_strip, Color(current_color['red'], current_color['blue'], current_color['green'], 1.0), 0, LED_LENGTH).run(1,30,50000)
    elif(sequence in ['PartyMode']):
	animations[sequence](led_strip, [Color(current_color['red'], current_color['blue'], current_color['green'], 1.0), wheel_color(43), wheel_color(17)], 0, LED_LENGTH).run(1,30,50000)
    elif(sequence in ['FireFlies']):
	animations[sequence](led_strip, [Color(current_color['red'], current_color['blue'], current_color['green'], 1.0), wheel_color(43), wheel_color(17)],1,1,0,LED_LENGTH).run(1,30,50000)
    elif(sequence in ['LarsonRainbow']):
	animations[sequence](led_strip, 2, 0.75, 0, 0).run(1,30,50000)
    elif(sequence in ['ColorFade']):
	animations[sequence](led_strip, [Color(current_color['red'], current_color['blue'], current_color['green'],1.0), wheel_color(317), wheel_color(13), wheel_color(133)], 0.1, 0, LED_LENGTH).run(1,30,50000)
    elif(sequence in ['ColorChase']):
	animations[sequence](led_strip, Color(current_color['red'], current_color['blue'], current_color['green'],1.0), 4, 0, LED_LENGTH).run(1,30,50000)
    elif(sequence in ['Wave']):
	animations[sequence](led_strip, Color(current_color['red'], current_color['blue'], current_color['green'], 1.0), 24).run(1,30,50000)
    elif(sequence in ['RGBClock']):
	animations[sequence](led_strip, 1, 12,13,73,74,160).run(1,30,50000)

    else:
        print "DO NOTHING"



@app.route('/set-strip-length', methods=['POST'])
def setStripLength():
    jd = json.loads(request.data)
    led_strip.all_off()
    led_strip = LEDStrip(LPD8806SPI(jd['length']))
    return "Strip length changed"

@app.route('/set-sequence', methods=['POST'])
def setSequence():
    jd = json.loads(request.data)
    print jd['sequence']
    print "Thread:"
    print procs
    if(len(procs)>=1):
	procs[0].terminate()
        procs.pop()
    #runSequenceInThread(jd['sequence'])
    current_proc = Process(target=runSequenceInThread, kwargs={'sequence':jd['sequence']})
    procs.append(current_proc)
    current_proc.start()
    return "set animation"


@app.route('/set-fade', methods=['POST'])
def setFade():
    jd = json.loads(request.data)
    print jd
    return "successfully set fade"

@app.route('/set-rgb', methods=['POST'])
def setrgb():
   jd = json.loads(request.data)
   current_color['red'] = int(jd['red'])
   current_color['green'] = int(jd['green'])
   current_color['blue'] = int(jd['blue'])
   print jd
   #led_strip.all_off()
   #response.headers.add('Access-Control-Allow-Origin', '*')    
   #print json.loads(response.data)['red']
   led_strip.fill(Color(int(jd['red']) , int(jd['blue']), int(jd['green']), 1.0))
   led_strip.update()
#   fa = FillFromCenter(led_strip, Color(int(jd['red']) , int(jd['green']), int(jd['blue']), 1.0))
 #  fa.run(1,30,18)

   return "ayyylmao"

@app.route('/')
def hello():
    alert_color = Color(255, 0, 0, 1.0)
    fill_animation = FillFromCenter(led_strip, alert_color)
    fill_animation.run(1, 30, 18)
    alert_animation = AlertStrobe(led_strip, alert_color)
    alert_animation.run(1, 20, 24)
    led_strip.all_off()
    fill_animation = BreathingLight(led_strip, 0, 255, 0, 0.1, 1.0, 0, 0)
    fill_animation.run(1, 30, 1000)
    led_strip.all_off()

    return "Hello World!"

if __name__ == '__main__':
    app.run(debug=True, port=3333, host='0.0.0.0')
