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


def ask(question, options):
    result = None
    while result not in options:
        print(question)
        result = input().strip()
    return result


def sensitivity_converter(sens):
    return{
        1: '70000',
        2: '63000',
        3: '57000',
        4: '50000',
        5: '45000',
        6: '38000',
        7: '26000',
        8: '20000',
        9: '11111',
        10: '0',
    }.get(sens,11)


# def askSL():
#     while True:
#         print("Please enter the SENSITIVITY to the amount of sound(): ")
#         print("Choose between 0 (Highest sense) to 44000(lowest): ")
#         sensLevel = int(input().strip())

#         if not sensLevel in range(0, 44000):
#             print("----------------INVALID VALUE--------------------")
#             askSL()
#         else:
#             False

#         return sensLevel


# answer = int(ask("Please enter the SENSITIVITY to the amount of sound from 1 to 10: ", [
#              "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]))

SENSITIVITY = int(sensitivity_converter(int(ask("Please enter the SENSITIVITY to the amount of sound from 1 to 10: ", [
             "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]))))
#print(type(SENSITIVITY))
#print(SENSITIVITY)
#SENSITIVITY = askSL()


def plot_data(in_data):
    global MUTE_LOCKED
    global VOLUME
    global MIXER

    # get and convert the data to float
    audio_data = struct.unpack("h", in_data[:2])
    ct = datetime.datetime.now()
    if audio_data[0] > SENSITIVITY:
        if VOLUME != 0:
            MIXER.setvolume(0)  # Set the volume to 0%.
            VOLUME = 0
            print("A voice of more than 60 DB Detected")
        MUTE_LOCKED = ct + MUTE_HOLD_TIME
    elif ct > MUTE_LOCKED:
        if VOLUME != 100:
            MIXER.setvolume(100)  # Set the volume to 100%.
            VOLUME = 100
            print("unmute_command")
    print("current time:-", ct)
    print("volume:", VOLUME)


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
