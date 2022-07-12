# pip install audiosegment numpy wave
from io import BytesIO
import sys
from datetime import datetime, timedelta
import audiosegment
import numpy as np
import os
import subprocess
import wave
from wwvbhelper import *

CENTURY = 2000

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = "output.wav"

f = wave.open(filename, 'rb')
channels = f.getnchannels()
samplerate = f.getframerate()
sample_width = f.getsampwidth()
frames = f.getnframes()
f.close()

duration = frames / samplerate

if sample_width == 2:
    buffertype = np.float16
else:
    buffertype = np.byte

# https://stackoverflow.com/questions/59365055/convert-file-into-bytesio-object-using-python
f = open(filename, "rb")
buffer = BytesIO(f.read())

print(samplerate)
print(duration)
    
# we are reading a window < 0.2 seconds stft, so that small errors in detecting the frame start point are essentially ignored; instead, we'll round to the nearest attenuation size for a given second by counting backwards when we see a de-attenuation occur to the last time a de-atteunuation ended
stft_sec = 0.05
stft_overlap = 0
stft_window = int(stft_sec * 1000) # audiosegment seems to use 1000 Hz window sampling rather than samplerate pre stft
full_window = int(1.0 / stft_sec) # one second window size post fft (each entry is worth stft_sec time)

# https://stackoverflow.com/questions/55635828/spectrogram-of-an-m4a-file
# https://stackoverflow.com/questions/55610891/numpy-load-from-io-bytesio-stream
buffernp = np.frombuffer(buffer.getbuffer(), dtype=buffertype)
seg = audiosegment.from_numpy_array(buffernp, samplerate) #.resample(sample_rate_Hz=samplerate,sample_width=2,channels=1)

#print(len(buffernp))
#print(seg)

target_amplitudes, timestamps = get_amplitudes(duration, stft_sec, stft_window, seg)

# print(*zip(timestamps, target_amplitudes))

values = get_frame_values(timestamps, target_amplitudes, full_window)
    
print(values)

hour, minute, doy, year, dst = decode(values)
year = year + CENTURY
month, day = doy2date(doy, year)

print("{}:{} on date {}/{} (day number {}) of {}, DST = {}".format(hour, minute, month, day, doy, year, dst))
