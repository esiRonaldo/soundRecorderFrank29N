import logging
import pyaudio
import struct
import sys
import datetime
import alsaaudio


FORMAT = pyaudio.paInt16  # We use 16bit format per sample
CHANNELS = 1
RATE = 44100
CHUNK = 1024  # 1024bytes of data red from a buffer

MIXER = alsaaudio.Mixer()
MUTE_HOLD_TIME = datetime.timedelta(seconds=5)
MUTE_LOCKED = datetime.datetime.min
VOLUME = None

# checking  the user input
def ask(question, options):
    result = None
    while result not in options:
        print(question)
        result = input().strip()
    return result

# binding the input to SENSITIVITY value
def sensitivity_converter(sens):
    return{
        1: '70000',
        2: '63000',
        3: '57000',
        4: '50000',
        5: '45000',
        6: '38000',
        7: '26000',
        8: '17000',
        9: '9500',
        10: '4000',
    }.get(sens, 11)


SENSITIVITY = int(sensitivity_converter(int(ask("Please enter the SENSITIVITY to the amount of sound from 1 to 10: ", [
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]))))


def plot_data(in_data):
    global MUTE_LOCKED
    global VOLUME
    global MIXER

    # get and convert the data to float
    audio_data = struct.unpack("h", in_data[:2])
    ct = datetime.datetime.now()
    
    #comparing the sensitivity with incoming noise
    if audio_data[0] > SENSITIVITY:
        if VOLUME != 0:
            MIXER.setmute(1)# Mute the system
           # MIXER.setvolume(0)  # Set the volume to 0% (MUTE).
            VOLUME = 0
            print("MUTED!!!")
        MUTE_LOCKED = ct + MUTE_HOLD_TIME
    
    elif ct > MUTE_LOCKED:
        if VOLUME != 100:
            MIXER.setmute(0)#Unmute the system
           # MIXER.setvolume(100)  # Set the volume to 100%.
            VOLUME = 100
            print("UNMUTED Again!!!")
            
    print("current time:-", ct)
    if VOLUME==0:
            print("MUTED!!!Noise higher than SENSITIVITY value")
    else:
        print('UNMUTE')
        
    #print("volume:", VOLUME)


def main():
    # making a LOGFILE
    logging.basicConfig(filename='logFile.log', level=logging.DEBUG)
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True)  # ,
    stream.start_stream()
    print("\n+---------------------------------+")
    print("| Press Ctrl+C to Break Recording |")
    print("+---------------------------------+\n")

    # Loop so program doesn't end while the stream callback's
    # itself for new data
    keep_going = True
    while keep_going:
        try:
            plot_data(stream.read(CHUNK, exception_on_overflow=False))
        except KeyboardInterrupt:
            keep_going = False

    # Close up shop (currently not used because KeyboardInterrupt
    # is the only way to close)
    stream.stop_stream()
    stream.close()

    audio.terminate()


if __name__ == "__main__":
    main()
