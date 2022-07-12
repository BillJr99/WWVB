# pip install youtube_dl urllib3 json pycurl audiosegment numpy pickle
import youtube_dl
import pycurl
from io import BytesIO
import sys
from datetime import datetime, timedelta
import audiosegment
import numpy as np
import os
import pickle
import subprocess

videourl = "https://www.youtube.com/watch?v=0m5AT67Apvs"
cachepath = "audio"

# The audio stream is pulse width modulated at 1000Hz
TARGET_FREQ = 1000 # 1000 Hz audio from WWVB

CENTURY = 2000

def get_value(arr, idx):
    if idx < len(arr):
        return arr[idx]
    else:
        return -1

def bcd(vals):
    result = -1
    
    indexes = [1, 2, 4, 8, 10, 20, 40, 80, 100, 200]
    
    if len(vals) > len(indexes):
        return result
    
    result = 0

    for k in range(len(vals)):
        if vals[k] != -1 and vals[k] != 2: # ignore errors and markers
            result = result + (vals[k] * indexes[k])
        
    return result

def decode(values):
    marker = get_value(values, 0)
    min40 = get_value(values, 1)
    min20 = get_value(values, 2)
    min10 = get_value(values, 3)
    blank = get_value(values, 4)
    min8 = get_value(values, 5)
    min4 = get_value(values, 6)
    min2 = get_value(values, 7)
    min1 = get_value(values, 8)
    blank = get_value(values, 9)
    blank = get_value(values, 10)
    blank = get_value(values, 11)
    hours20 = get_value(values, 12)
    hours10 = get_value(values, 13)
    blank = get_value(values, 14)
    hours8 = get_value(values, 15)
    hours4 = get_value(values, 16)
    hours2 = get_value(values, 17)
    hours1 = get_value(values, 18)
    blank = get_value(values, 19)
    blank = get_value(values, 20)
    blank = get_value(values, 21)
    doy200 = get_value(values, 22)
    doy100 = get_value(values, 23)
    blank = get_value(values, 24)
    doy80 = get_value(values, 25)
    doy40 = get_value(values, 26)
    doy20 = get_value(values, 27)
    doy10 = get_value(values, 28)
    blank = get_value(values, 29)
    doy8 = get_value(values, 30)
    doy4 = get_value(values, 31)
    doy2 = get_value(values, 32)
    doy1 = get_value(values, 33)
    blank = get_value(values, 34)
    blank = get_value(values, 35)
    dut1plus1 = get_value(values, 36)
    dut1minus = get_value(values, 37)
    dut1plus2 = get_value(values, 38)
    blank = get_value(values, 39)
    dut1point8 = get_value(values, 40)
    dut1point4 = get_value(values, 41)
    dut1point2 = get_value(values, 42)
    dut1point1 = get_value(values, 43)
    blank = get_value(values, 44)
    year80 = get_value(values, 45)
    year40 = get_value(values, 46)
    year20 = get_value(values, 47)
    year10 = get_value(values, 48)
    blank = get_value(values, 49)
    year8 = get_value(values, 50)
    year4 = get_value(values, 51)
    year2 = get_value(values, 52)
    year1 = get_value(values, 53)
    blank = get_value(values, 54)
    leapyear = get_value(values, 55)
    leapsecond = get_value(values, 56)
    dstupper = get_value(values, 57)
    dstlower = get_value(values, 58)
    marker = get_value(values, 59)
    
    print("min40 = {}".format(min40))
    print("min20 = {}".format(min20))
    print("min10 = {}".format(min10))
    print("min8 = {}".format(min8))
    print("min4 = {}".format(min4))
    print("min2 = {}".format(min2))
    print("min1 = {}".format(min1))
    
    print("hours20 = {}".format(hours20))
    print("hours10 = {}".format(hours10))
    print("hours8 = {}".format(hours8))
    print("hours4 = {}".format(hours4))
    print("hours2 = {}".format(hours2))
    print("hours1 = {}".format(hours1))  

    print("doy200 = {}".format(doy200))
    print("doy100 = {}".format(doy100))
    print("doy80 = {}".format(doy80))
    print("doy40 = {}".format(doy40))
    print("doy20 = {}".format(doy20))
    print("doy10 = {}".format(doy10))
    print("doy8 = {}".format(doy8))
    print("doy4 = {}".format(doy4))
    print("doy2 = {}".format(doy2))
    print("doy1 = {}".format(doy1))   

    print("year80 = {}".format(year80))
    print("year40 = {}".format(year40))
    print("year20 = {}".format(year20))
    print("year10 = {}".format(year10))
    print("year8 = {}".format(year8))
    print("year4 = {}".format(year4))
    print("year2 = {}".format(year2))
    print("year1 = {}".format(year1))    
    
    hour = bcd([hours1, hours2, hours4, hours8, hours10, hours20])
    minute = bcd([min1, min2, min4, min8, min10, min20, min40])
    
    # add 1 minute after the signal is received, since the timestamp began when the transmission began
    minute = minute + 1
    
    doy = bcd([doy1, doy2, doy4, doy8, doy10, doy20, doy40, doy80, doy100, doy200])
    year = bcd([year1, year2, year4, year8, year10, year20, year40, year80])
    
    # dst = dstupper_dstlower (00 = ST, 01 = DT ending, 10 = DT beginning, 11 = DT)
    if dstupper == 0 and dstlower == 0:
        dst = False
    else:
        dst = True
        
    return hour, minute, doy, year, dst
    
def identify_bit(wnd, wndtimes, time_delta, threshold=0.5, tolerance=1):
    wnd = (wnd - np.min(wnd)) / (np.max(wnd) - np.min(wnd)) # 0-1 normalize the window
    print(*zip(wndtimes, wnd))

    violations = 0
    count = 0
    for i in range(len(wnd)):
        valid = True
        
        if wnd[i] < threshold:
            violations = violations + 1
            
            if violations >= tolerance:
                valid = False
        
        if valid:
            count = count + 1
        else:
            count = 0
            violations = 0
    
    # we were counting backwards (the longest run of high values at the end)
    # WWVB counts according to the duration UNTIL the signal goes high
    count = len(wnd) - count
    
    print("lowtime = {}".format((count * time_delta)))
    
    # binary 0 is attenuation for 200ms, binary 1 is attenuation for 500ms, marker is attenuation for 800ms, which we represent as 2; -1 is error
    if count * time_delta < 0.1:
        result = -1
    elif count * time_delta < 0.35:
        result = 0
    elif count * time_delta < 0.65:
        result = 1
    else:
        result = 2
        
    return result

def getbit(timestamps, target_amplitudes, idx):
    result = -1 
    
    if len(timestamps) < 2 or idx + 1 > len(timestamps) or idx < 0:
        return result
        
    starting_timestamp = timestamps[idx]
    if idx > len(timestamps) - 1:
        time_delta = timestamps[idx-1] - timestamps[idx]
    else:
        time_delta = timestamps[idx+1] - timestamps[idx]
    
    #print(starting_timestamp)
    #print(time_delta)
    
    wnd = []
    wndtimes = []
    
    k = idx
    while k >= 0 and k < len(target_amplitudes) and k < len(timestamps) and timestamps[k] < 1 + starting_timestamp:
        wnd.append(target_amplitudes[k])
        wndtimes.append(timestamps[k])
        k = k + 1

    if len(wnd) == 0:
        return result
        
    result = identify_bit(wnd, wndtimes, time_delta)
    
    # return the bit and the length of the window read (so it can be advanced)
    return result

# https://stackoverflow.com/questions/64025789/python-how-to-convert-day-of-year-to-day-and-month#:~:text=%22%22%22calculate%20day%20and%20month,month%20day%20%3D%20endDate.
# https://stackoverflow.com/questions/61810757/find-total-number-of-days-in-a-year-pandas
def doy2date(doy, YEAR):
    startDate = datetime(year=YEAR, month=1, day=1)
    endDate = startDate + timedelta(days=doy-1) # count from day 1 not 0

    month = endDate.month
    day = endDate.day

    return month, day

# https://stackoverflow.com/questions/19724222/pycurl-attachments-and-progress-functions
# callback function for c.XFERINFOFUNCTION
def status(download_t, download_d, upload_t, upload_d, STREAM=sys.stderr, kb=1024):
    STREAM.write('Downloading: {}/{} kiB ({}%)\r'.format(
        str(int(download_d/kb)),
        str(int(download_t/kb)),
        str(int(download_d/download_t*100) if download_t > 0 else 0)
    ))
    STREAM.flush()
    
if not (os.path.exists(cachepath + ".m4a") and os.path.exists(cachepath + ".pickle")):
    # https://github.com/ytdl-org/youtube-dl/blob/master/README.md#embedding-youtube-dl
    # https://stackoverflow.com/questions/18054500/how-to-use-youtube-dl-from-a-python-program
    ydl = youtube_dl.YoutubeDL({})

    with ydl:
        result = ydl.extract_info(
            videourl,
            download=False # We just want to extract the info
        )

    if 'entries' in result:
        # Can be a playlist or a list of videos
        video = result['entries'][0]
    else:
        # Just a video
        video = result

    audiourl = None
    samplerate = 0
    duration = video['duration']

    for format in video['formats']:
        if format['ext'] == 'm4a':
            audiourl = format['url']
            samplerate = format['asr']
            break
      
    #print(audiourl)

    if audiourl is None:
        sys.exit(0)
        
    # https://stackoverflow.com/questions/39551320/python-download-video-from-indirect-url 
    # http://pycurl.io/docs/latest/quickstart.html
    # https://stackoverflow.com/questions/19724222/pycurl-attachments-and-progress-functions
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.FOLLOWLOCATION, 1)
    c.setopt(c.URL, audiourl)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.VERBOSE, True)
    # display progress
    c.setopt(c.NOPROGRESS, False)
    c.setopt(c.XFERINFOFUNCTION, status)
    c.perform()

    #print(buffer)
    # cache the buffer
    with open(cachepath + ".m4a", "wb") as f:
        f.write(buffer.getbuffer())
        
    # cache the metadata
    metadata = {"samplerate": samplerate, "duration": duration}
    with open(cachepath + ".pickle", "wb") as f:
        pickle.dump(metadata, f, protocol=pickle.HIGHEST_PROTOCOL)

# https://www.tutorialexample.com/converting-m4a-to-wav-using-pydub-in-python-python-tutorial/
if not os.path.exists(cachepath + ".wav"):
    cmd = "ffmpeg -i " + cachepath + '.m4a' + " " + cachepath + '.wav'
    subprocess.run(cmd.split())
    
f = open(cachepath + ".pickle", "rb")
p = pickle.load(f)
samplerate = p['samplerate']
duration = p['duration']

# https://stackoverflow.com/questions/59365055/convert-file-into-bytesio-object-using-python
f = open(cachepath + ".wav", "rb")
buffer = BytesIO(f.read())

#print(samplerate)
#print(duration)
    
# we are reading a window < 0.2 seconds stft, so that small errors in detecting the frame start point are essentially ignored; instead, we'll round to the nearest attenuation size for a given second by counting backwards when we see a de-attenuation occur to the last time a de-atteunuation ended
stft_sec = 0.05
stft_overlap = 0
stft_window = int(stft_sec * 1000) # audiosegment seems to use 1000 Hz window sampling rather than samplerate pre stft
full_window = int(1.0 / stft_sec) # one second window size post fft (each entry is worth stft_sec time)

# https://stackoverflow.com/questions/55635828/spectrogram-of-an-m4a-file
# https://stackoverflow.com/questions/55610891/numpy-load-from-io-bytesio-stream
buffernp = np.frombuffer(buffer.getbuffer(), dtype=np.float16)
seg = audiosegment.from_numpy_array(buffernp, samplerate) #.resample(sample_rate_Hz=samplerate,sample_width=2,channels=1)

#print(len(buffernp))
#print(seg)

target_amplitudes = []
timestamps = []

i = 0
while i < int(duration / stft_sec): 
    #print("{}: {} to {}".format(i, i*stft_window, (i+1)*stft_window))
    
    wnd = seg[i*stft_window:(i+1)*stft_window]
    #print(wnd)
    
    # https://readthedocs.org/projects/audiosegment/downloads/pdf/latest/
    freqs, amplitudes = wnd.fft()
    amplitudes = np.abs(amplitudes) / len(amplitudes)
        
    # find the bin index corresponding to our target frequency
    binidx=0
    for k in range(1, len(freqs)):
        if abs(freqs[k] - TARGET_FREQ) > abs(freqs[k-1] - TARGET_FREQ):
            binidx = k-1
            break
            
    #print("{} {}".format(i*stft_sec, amplitudes[binidx]))
    
    target_amplitudes.append(amplitudes[binidx])
    timestamps.append(i * stft_sec)
    
    i = i + 1

# print(*zip(timestamps, target_amplitudes))

idx = 0
currentbit = -1

values = []

# Look for starting marker (2).  Really there should be 2 in a row to be sure it's the starting marker
while not (currentbit == 2):
    currentbit = getbit(timestamps, target_amplitudes, idx)
    
    print("{}: {}".format(idx, currentbit))
    print("=============")
    
    idx = idx + 1 # advance by 1 while searching for start marker

values.append(currentbit)
idx = idx + full_window - 1 # advance by 1 second on successful starting marker decode, taking away 1 for the 1 we advanced in the loop already

# WWVB sends an end marker at the end and for some of the blanks, but you should reach the end of any prerecorded single signal input, and really you should also get 60 decodes ending with a marker followed by a second consecutive marker for the start of the next signal
while len(values) < 60 and idx < len(target_amplitudes) and idx < len(timestamps):
    currentbit = getbit(timestamps, target_amplitudes, idx)
    
    print("{}: {}".format(idx, currentbit))
    print("=============")
    
    values.append(currentbit) # append successful decode to the list; ignore error bits

    idx = idx + full_window # advance by 1 second window
    
print(values)

hour, minute, doy, year, dst = decode(values)
year = year + CENTURY
month, day = doy2date(doy, year)

print("{}:{} on date {}/{} (day number {}) of {}, DST = {}".format(hour, minute, month, day, doy, year, dst))
