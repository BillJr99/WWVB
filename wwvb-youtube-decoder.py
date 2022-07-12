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
from wwvbhelper import *

videourl = "https://www.youtube.com/watch?v=0m5AT67Apvs"
cachepath = "audio"

CENTURY = 2000

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

target_amplitudes, timestamps = get_amplitudes(duration, stft_sec, stft_window, seg)

# print(*zip(timestamps, target_amplitudes))

values = get_frame_values(timestamps, target_amplitudes, full_window)
    
print(values)

hour, minute, doy, year, dst = decode(values)
year = year + CENTURY
month, day = doy2date(doy, year)

print("{}:{} on date {}/{} (day number {}) of {}, DST = {}".format(hour, minute, month, day, doy, year, dst))
