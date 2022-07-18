# https://stackoverflow.com/questions/18625085/how-to-plot-a-wav-file

import matplotlib.pyplot as plt
import numpy as np
import wave
import sys

if len(sys.argv) < 2:
    print("Usage: wavplot.py <audio file>")

spf = wave.open(sys.argv[1], "r")

sample_width = spf.getsampwidth()
if sample_width == 2:
    buffertype = np.int16 # was float16
else:
    buffertype = np.byte
    
fs = spf.getframerate()    

# Extract Raw Audio from Wav File
signal = spf.readframes(-1)
signal = np.fromstring(signal, buffertype)

# If Stereo
if spf.getnchannels() == 2:
    print("Just mono files")
    sys.exit(0)
    
Time = np.linspace(0, len(signal) / fs, num=len(signal))

plt.figure(1)
plt.title("Signal Wave...")
plt.plot(Time, signal)
plt.show()
