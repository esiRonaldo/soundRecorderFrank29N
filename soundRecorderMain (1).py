try:
    import logging
    import pyaudio
    import numpy as np
    import pylab
    import matplotlib.pyplot as plt
    from scipy.io import wavfile
    from playsound import playsound  # mp3 player
    import time
    import sys
    import datetime
    import seaborn as sns
    import wave
    import alsaaudio
except:
    print("Something didn't import")
# pip install --upgrade matplotlib
# if you cant install pyaudio try this=> sudo apt-get install portaudio19-dev

# ct stores current time
ct = datetime.datetime.now()
# mute variable
m = alsaaudio.Mixer()

i = 0
f, ax = plt.subplots(2)
# Prepare the Plotting Environment with random starting values
x = np.arange(10000)
y = np.random.randn(10000)

# Plot 0 is for raw audio data
li, = ax[0].plot(x, y)
ax[0].set_xlim(0, 1000)
ax[0].set_ylim(-5000, 5000)
ax[0].set_title("Raw Audio Signal")
# Plot 1 is for the FFT of the audio
li2, = ax[1].plot(x, y)
ax[1].set_xlim(0, 5000)
ax[1].set_ylim(-100, 100)
ax[1].set_title("Fast Fourier Transform")
# Show the plot, but without blocking updates
plt.pause(0.01)
plt.tight_layout()

# making a LOGFILE 
logging.basicConfig(filename='logFile.log', level=logging.DEBUG)
#logging.DEBUG("Q")

FORMAT = pyaudio.paInt16  # We use 16bit format per sample
CHANNELS = 1
RATE = 44100
CHUNK = 1024  # 1024bytes of data red from a buffer
RECORD_SECONDS = 0.1
WAVE_OUTPUT_FILENAME = "file.wav"

audio = pyaudio.PyAudio()

# start Recording
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True)  # ,
# frames_per_buffer=CHUNK)


global keep_going
keep_going = True

global waitingBool
waitingBool= False

# sleep method
def micWaiting(seconds):
    for count in range(seconds):
        print(time.ctime())
        time.sleep(count)


def plot_data(in_data):
    # get and convert the data to float
    audio_data = np.fromstring(in_data, np.int16)
    # Fast Fourier Transform, 10*log10(abs) is to scale it to dB
    # and make sure it's not imaginary
    dfft = 10. * np.log10(abs(np.fft.rfft(audio_data)))

    # Force the new data into the plot, but without redrawing axes.
    # If uses plt.draw(), axes are re-drawn every time

    if audio_data[0] > 18000:
        print("A voice of more than 6000 DB Detected")
        # sys_message(mute_command)
        m.setvolume(0)  # Set the volume to 0%.
        waitingBool=True
        micWaiting(5)
        waitingBool=False
        logging.debug('mutedd_command_Current time:- {}'.format(ct))
        print("current time:-", ct)

    elif audio_data[0] < 10:
       # micWaiting(7)
        m.setvolume(100)  # Set the volume to 100%.
        logging.debug('Unmutedd_command_Current time:- {}'.format(ct))
        print("unmute_command")


    else:
        print("In spaeking range")
        #micWaiting(5)
        m.setvolume(100)  # Set the volume to 100%.
        logging.debug('Unmutedd_command_Current time:- {}'.format(ct))
        print("unmute_command")

    # ----------------saving the record as a wave file based on the--------------
    # wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    # wf.setnchannels(CHANNELS)
    # wf.setsampwidth(audio.get_sample_size(FORMAT))
    # wf.setframerate(RATE)
    # wf.writeframes(b''.join(frames))
    # wf.close()
    # print audio_data[0:10]
    # print dfft[0:10]
    # print

    #-------------PLOT cordinates----------
   # li.set_xdata(np.arange(len(audio_data)))
    #li.set_ydata(audio_data)
    #li2.set_xdata(np.arange(len(dfft)) * 10.)
    #li2.set_ydata(dfft)

    # Show the updated plot, but without blocking
    plt.pause(0.01)
    if keep_going:
        return True
    else:
        return False


# Open the connection and start streaming the data
stream.start_stream()
print("\n+---------------------------------+")
print("| Press Ctrl+C to Break Recording |")
print("+---------------------------------+\n")
# -----------------Playing some MP3 (all functions wait for this)-----------------
# playsound('Amir Tataloo - Ba To.mp3')

# Loop so program doesn't end while the stream callback's
# itself for new data
while keep_going:
    try:
        waitingBool= False
        plot_data(stream.read(CHUNK, exception_on_overflow=False))
    except KeyboardInterrupt:
        keep_going = False
    except:
        pass

# Close up shop (currently not used because KeyboardInterrupt
# is the only way to close)
stream.stop_stream()
stream.close()

audio.terminate()
