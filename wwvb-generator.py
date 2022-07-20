# pip install pyaudio wave
from __future__ import division
from pyaudio import PyAudio
import math
try:
    from itertools import izip
except ImportError: # Python 3
    izip = zip
    xrange = range
from itertools import chain
import datetime
import time
import wave

# https://www.tutorialspoint.com/read-and-write-wav-files-using-python-wave
def save_stream(samples, sample_rate=44100, filename="output.wav"):
    f = wave.open(filename, 'wb')
    f.setnchannels(1)
    f.setframerate(sample_rate)
    f.setsampwidth(1)
 
    n = 0
    
    for buf in izip(*[samples]*sample_rate): # write several samples at a time
        data = bytes(bytearray(buf))
        n = n + len(data)
        f.writeframesraw(data) 
    
    f.close()
    
# https://stackoverflow.com/questions/974071/python-library-for-playing-fixed-frequency-sound    
def play_stream(samples, sample_rate=44100):
    p = PyAudio()
    stream = p.open(format=p.get_format_from_width(1), # 8bit
                    channels=1, # mono
                    rate=sample_rate,
                    output=True)
                    
    for buf in izip(*[samples]*sample_rate): # write several samples at a time
        stream.write(bytes(bytearray(buf)))

    stream.stop_stream()
    stream.close()
    p.terminate()                    

# https://stackoverflow.com/questions/974071/python-library-for-playing-fixed-frequency-sound
def sine_tone_sine_tone(frequency1, duration1, frequency2, duration2, volume1=1, volume2=1, sample_rate=44100):
    n_samples1 = int(sample_rate * duration1)
    n_samples2 = int(sample_rate * duration2)
    
    restframes = (n_samples1 + n_samples2) % sample_rate

    s1 = lambda t: volume1 * math.sin(2 * math.pi * frequency1 * t / sample_rate)
    samples1 = (int(s1(t) * 0x7f + 0x80) for t in xrange(n_samples1))

    s2 = lambda t: volume2 * math.sin(2 * math.pi * frequency2 * t / sample_rate)
    samples2 = (int(s2(t) * 0x7f + 0x80) for t in xrange(n_samples2))
    
    restsamples = (int(0x80) for i in xrange(restframes))

    return samples1, samples2, restsamples
    
def gen_marker():
    print("2")
    s1, s2, rs = sine_tone_sine_tone(1000, 0.8, 1000, 0.2, volume1=0.8, volume2=0.2)
    return s1, s2, rs

def gen_one():
    print("1")
    s1, s2, rs = sine_tone_sine_tone(1000, 0.5, 1000, 0.5, volume1=0.8, volume2=0.2)
    return s1, s2, rs

def gen_zero():
    print("0")
    s1, s2, rs = sine_tone_sine_tone(1000, 0.2, 1000, 0.8, volume1=0.8, volume2=0.2)
    return s1, s2, rs

def append_tones(generator, sounds):
    s1, s2, rs = generator()
    sounds.append(s1)
    sounds.append(s2)
    sounds.append(rs)    
    return sounds

def bcd_tone(sounds, value, threshold):
    if value >= threshold:
        sounds = append_tones(gen_one, sounds)
        value = value - threshold
    else:
        sounds = append_tones(gen_zero, sounds)
        
    return sounds, value

now = datetime.datetime.now().utcnow() # 2021-11-13 23:30:38.419951

year = now.year
leapyear = False
if (year % 400 == 0) and (year % 100 == 0):
    leapyear = True
elif (year % 4 ==0) and (year % 100 != 0):
    leapyear = True
year = year % 100 # last 2 digits
month = now.month
day = now.day
hours = now.hour
minutes = now.minute
dst = time.localtime().tm_isdst
doy = int(now.strftime('%j'))

sounds = []

sounds = append_tones(gen_marker, sounds)
sounds, minutes = bcd_tone(sounds, minutes, 40)
sounds, minutes = bcd_tone(sounds, minutes, 20)
sounds, minutes = bcd_tone(sounds, minutes, 10)
sounds = append_tones(gen_zero, sounds)
sounds, minutes = bcd_tone(sounds, minutes, 8)
sounds, minutes = bcd_tone(sounds, minutes, 4)
sounds, minutes = bcd_tone(sounds, minutes, 2)
sounds, minutes = bcd_tone(sounds, minutes, 1)
sounds = append_tones(gen_marker, sounds)
sounds = append_tones(gen_zero, sounds)
sounds = append_tones(gen_zero, sounds)
sounds, hours = bcd_tone(sounds, hours, 20)
sounds, hours = bcd_tone(sounds, hours, 10)
sounds = append_tones(gen_zero, sounds)
sounds, hours = bcd_tone(sounds, hours, 8)
sounds, hours = bcd_tone(sounds, hours, 4)
sounds, hours = bcd_tone(sounds, hours, 2)
sounds, hours = bcd_tone(sounds, hours, 1)
sounds = append_tones(gen_marker, sounds)
sounds = append_tones(gen_zero, sounds)
sounds = append_tones(gen_zero, sounds)
sounds, doy = bcd_tone(sounds, doy, 200)
sounds, doy = bcd_tone(sounds, doy, 100)
sounds = append_tones(gen_zero, sounds)
sounds, doy = bcd_tone(sounds, doy, 80)
sounds, doy = bcd_tone(sounds, doy, 40)
sounds, doy = bcd_tone(sounds, doy, 20)
sounds, doy = bcd_tone(sounds, doy, 10)
sounds = append_tones(gen_zero, sounds)
sounds, doy = bcd_tone(sounds, doy, 8)
sounds, doy = bcd_tone(sounds, doy, 4)
sounds, doy = bcd_tone(sounds, doy, 2)
sounds, doy = bcd_tone(sounds, doy, 1)
sounds = append_tones(gen_zero, sounds)
sounds = append_tones(gen_zero, sounds)
sounds = append_tones(gen_zero, sounds) # dut+
sounds = append_tones(gen_zero, sounds) # dut-
sounds = append_tones(gen_zero, sounds) # dut+
sounds = append_tones(gen_marker, sounds) 
sounds = append_tones(gen_zero, sounds) # dut 0.8
sounds = append_tones(gen_zero, sounds) # dut 0.4
sounds = append_tones(gen_zero, sounds) # dut 0.2
sounds = append_tones(gen_zero, sounds) # dut 0.1
sounds = append_tones(gen_zero, sounds)
sounds, year = bcd_tone(sounds, year, 80)
sounds, year = bcd_tone(sounds, year, 40)
sounds, year = bcd_tone(sounds, year, 20)
sounds, year = bcd_tone(sounds, year, 10)
sounds = append_tones(gen_marker, sounds) 
sounds, year = bcd_tone(sounds, year, 8)
sounds, year = bcd_tone(sounds, year, 4)
sounds, year = bcd_tone(sounds, year, 2)
sounds, year = bcd_tone(sounds, year, 1)
sounds = append_tones(gen_zero, sounds)
if leapyear:
    sounds = append_tones(gen_one, sounds)
else:
    sounds = append_tones(gen_zero, sounds)
sounds = append_tones(gen_zero, sounds) # leap second    
if dst == 1:
    sounds = append_tones(gen_one, sounds)
    sounds = append_tones(gen_one, sounds)
else:
    sounds = append_tones(gen_zero, sounds)
    sounds = append_tones(gen_zero, sounds)
sounds = append_tones(gen_marker, sounds)

samples = chain(*sounds)
#play_stream(samples)
save_stream(samples)